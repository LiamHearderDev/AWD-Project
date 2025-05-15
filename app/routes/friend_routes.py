from flask import (
    render_template, redirect, flash,
    url_for, request, abort, jsonify, Blueprint
)
from flask_login import login_required, current_user
from app import db
from app.models import User, Friendship
from app.forms import FriendRequestForm
from app.routes.stats_routes import compute_user_stats, format_data

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/friends', methods=['GET','POST'])
@login_required
def friends():
    # two prefixes to avoid name collisions
    form = FriendRequestForm()

    # Get all current friends
    friends = Friendship.query.filter_by(user_id=current_user.user_id, is_requested=False).all()

    # Get all incoming friend requests
    friend_requests = Friendship.query.filter_by(user_id=current_user.user_id, is_requested=True).filter(Friendship.requesting_user != current_user.user_id).all()

    # Short helper function to avoid repeated code
    def render_friends_page():
        return render_template('friends/friends.html',
            form=form,
            friend_requests=friend_requests,
            friends=friends
        )
    
    # Check if the form isn't validated. If not, load the page as normal.
    if not form.validate_on_submit():
        return render_friends_page()
    
    # Get the user we are sending a friend request to.

    target_username = form.username.data
    target_user = User.query.filter_by(username=target_username).first()

    if not target_user:
        flash("User not found.")
        return render_friends_page()
    
    if target_user.user_id == current_user.user_id:
        flash("You cannot send a request to yourself.")
        return render_friends_page()
    
    # Stops the request if you already sent them a request, or are already friends.
    existing_friendship = Friendship.query.get((current_user.user_id, target_user.user_id))
    if existing_friendship:
        if existing_friendship.is_requested == True:
            flash(f"You have already sent {target_user.username} user a friend request.")
        else:
            flash(f"You are already friends with this {target_user.username}.")
        return render_friends_page()
    
    # Creates a new friendship object to be stored by the current user
    local_friendship_object = Friendship(
        user_id=current_user.user_id,
        friend_id=target_user.user_id,
        is_requested=True,
        requesting_user=current_user.user_id
    )

    # Creates a new friendship object to be stored by the receiving friend
    sent_friendship_object = Friendship(
        user_id=target_user.user_id,
        friend_id=current_user.user_id,
        is_requested=True,
        requesting_user=current_user.user_id
    )

    # Commits it to the db
    db.session.add(local_friendship_object) # The friend request
    db.session.add(sent_friendship_object)  # The friend request sent to the friend
    db.session.commit()

    flash("Friend request sent!")
    return render_friends_page()


@friends_bp.route('/friends/<acceptance>-request', methods=['POST'])
@login_required
def handle_friend_request(acceptance: str):
    """
    Accept or reject a pending request from sender -> current_user.
    """
    # If someone accesses an invalid URL, they need to be stopped here.
    if acceptance not in ["accept", "reject"]:
        abort(404)
        return jsonify(success=False, message=f"Invalid URL. Acceptance={acceptance}")
    
    # Get the data sent over by the AJAX request.
    # If the payload is None, there has been an error.
    payload = request.get_json(silent=True)
    if payload == None:
        flash("An error occurred while handling a friend request. Please try again later.", "error")
        return jsonify(success=False, message='Could not extract payload from request.')

    # Extract the data from the payload. This is the user_id from the user who sent the friend request.
    sender_id = payload["sender_id"]

    # Look up the pending request as it exists on the friend's ID.
    friend_relation = Friendship.query.get((sender_id, current_user.user_id))

    # Find the pending request as it exists on the current_user's ID.
    current_user_relation = Friendship.query.get((current_user.user_id, sender_id))

    # Exit early if no such friend request is in the database
    if friend_relation == None or current_user_relation == None:
        flash("An error occurred while handling a friend request. Please try again later.", "error")
        return jsonify(success=False, message=f"Could not find valid friend request in the database. current_user.user_id={current_user.user_id}, friend_id={sender_id}.")
    
    # Exit early if the friend request has already been accepted
    if friend_relation.is_requested == False or current_user_relation.is_requested == False:
        flash("This friend request has already been accepted.", "error")
        return jsonify(success=False, message='Invalid request. Friend request had already been accepted.')
    
    # If the user is trying to reject the 
    if acceptance == "reject":
        db.session.delete(friend_relation)
        db.session.delete(current_user_relation)
        db.session.commit()
        return jsonify(success=True, message='Successfully rejected friend request.')
    elif acceptance == "accept":
        # mark as accepted and add reciprocal row
        friend_relation.is_requested = False
        current_user_relation.is_requested = False
        db.session.commit()
        return jsonify(success=True, message='Successfully accepted friend request.')


# There is no reason reason to have a block function, as users can't send each other messages

# @friends_bp.route('/friends/block/<int:sender_id>', methods=['POST'])
# @login_required
# def block_friend(sender_id):
#     """
#     Reject/block (i.e. delete) a pending request from sender_id -> you.
#     """
#     relation = Friendship.query.get((sender_id, current_user.user_id))
#     if not relation or relation.is_requested:
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return jsonify(success=False, message='Invalid block request.')
#         abort(404)

#     db.session.delete(relation)
#     db.session.commit()

#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return jsonify(success=True)

#     flash('Friend request rejected.', 'info')
#     return redirect(url_for('friends.friends'))


@friends_bp.route('/friends/<friend_username>/stats')
@login_required
def view_friend_stats(friend_username: str):
    """
    Show friend's stats if confirmed friend.
    """
    # If no username has been provided, 404 error
    if not friend_username:
        abort(404)

    # If the provided username is the current_user's username, redirect to the normal stats page
    if friend_username == current_user.username:
        return redirect(url_for('stats.stats'))

    # Get the friend's user
    friend: User = User.query.filter_by(username=friend_username).first()

    # Find the friendship row
    relation: Friendship = Friendship.query.get((current_user.user_id, friend.user_id))

    # If no friendship was found, give an error
    if not relation:
        abort(404)
    
    # If the friendship hasn't been accepted, give an error
    if relation.is_requested:
        abort(403)
        

    # Compute stats using days parameter per compute_user_stats signature
    stats_today  = compute_user_stats(friend.user_id, days=0)
    stats_7days  = compute_user_stats(friend.user_id, days=7)
    stats_28days = compute_user_stats(friend.user_id, days=28)
    stats_all    = compute_user_stats(friend.user_id, days=None)

    return render_template(
        'friends/friends_stats.html',
        username=friend.username,
        today_table=format_data(stats_today, 'table'),
        last7_table=format_data(stats_7days, 'table'),
        last28_table=format_data(stats_28days, 'table'),
        alltime_table=format_data(stats_all, 'table'),
        today_chart=format_data(stats_today, 'chart'),
        last7_chart=format_data(stats_7days, 'chart'),
        last28_chart=format_data(stats_28days, 'chart'),
        alltime_chart=format_data(stats_all, 'chart')
    )

@friends_bp.route('/friends/remove/<int:friend_id>', methods=['GET','POST'])
@login_required
def remove_friend(friend_id):
    """
    Unfriend: delete both A->B and B->A rows.
    """
    # find both sides
    relationship1: Friendship | None = Friendship.query.get((current_user.user_id, friend_id))
    relationship2: Friendship | None = Friendship.query.get((friend_id, current_user.user_id))

    # If either relationship is invalid, flash an error.
    if not relationship1 or not relationship2:
        flash("You are currently not friends with this user.", "error")
        
        # If only one relationship is None, there has been a major database error that must be fixed. Remove whichever is valid.
        if relationship1 != relationship2:
            valid_relationship: Friendship = relationship1 if relationship1 != None else relationship2
            db.session.delete(valid_relationship)
            db.session.commit()

        return redirect(url_for('friends.friends'))
    
    # If either relationship is just a request, flash an error.
    if relationship1.is_requested or relationship2.is_requested:
        flash("You are currently not friends with this user.", "error")

        # If only one relationship is a request, there has been a major database error that must be fixed. Remove them both. 
        if relationship1.is_requested != relationship2.is_requested:
            db.session.delete(relationship1)
            db.session.delete(relationship2)
            db.session.commit()

        return redirect(url_for('friends.friends'))
    
    # delete both
    db.session.delete(relationship1)
    db.session.delete(relationship2)
    db.session.commit()

    # fallback for normal form
    return redirect(url_for('friends.friends'))