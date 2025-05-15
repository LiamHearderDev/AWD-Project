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
    friend_requests = Friendship.query.filter_by(friend_id=current_user.user_id, is_requested=True).all()

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
    
    # Creates a new friendship object
    friendship_object = Friendship(
        user_id=current_user.user_id,
        friend_id=target_user.user_id,
        is_requested=True,
        requesting_user=current_user.user_id
    )

    # Commits it to the db
    db.session.add(friendship_object)
    db.session.commit()

    flash("Friend request sent!")
    return render_friends_page()


@friends_bp.route('/friends/accept/<int:sender_id>', methods=['POST'])
@login_required
def accept_friend(sender_id):
    """
    Accept a pending request from sender_id → you.
    Returns JSON for AJAX or does a flash+redirect if non-XHR.
    """
   # Look up the pending request from sender → you
    relation = Friendship.query.get((sender_id, current_user.user_id))

    # If it doesn’t exist OR it’s already accepted (is_requested=True), reject
    if not relation or relation.is_requested:
        ##X-Requested-With is a convention many JavaScript libraries (and browsers’ fetch when you set it) use to label AJAX/XHR calls.
        ## By checking == 'XMLHttpRequest',  server knows “this came from JS, not a direct browser navigation or form submit
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
            return jsonify(success=False, message='Invalid request.')
        abort(404)

    # mark as accepted and add reciprocal row
    relation.is_requested = True
    reciprocal = Friendship(
        user_id=current_user.user_id,
        friend_id=sender_id,
        is_requested=True,
        requesting_user=relation.requesting_user
    )
    db.session.add(reciprocal)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)

    flash('Friend request accepted!', 'success')
    return redirect(url_for('friends.friends'))

@friends_bp.route('/friends/block/<int:sender_id>', methods=['POST'])
@login_required
def block_friend(sender_id):
    """
    Reject/block (i.e. delete) a pending request from sender_id → you.
    """
    relation = Friendship.query.get((sender_id, current_user.user_id))
    if not relation or relation.is_requested:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message='Invalid block request.')
        abort(404)

    db.session.delete(relation)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)

    flash('Friend request rejected.', 'info')
    return redirect(url_for('friends.friends'))

@friends_bp.route('/friends/<int:friend_id>/stats')
@login_required
def view_friend_stats(friend_id):
    """
    Show friend's stats if confirmed friend.
    """
    relation = Friendship.query.get((current_user.user_id, friend_id))
    if not relation or not relation.is_requested:
        abort(403)

    # Compute stats using days parameter per compute_user_stats signature
    stats_today  = compute_user_stats(friend_id, days=0)
    stats_7days  = compute_user_stats(friend_id, days=7)
    stats_28days = compute_user_stats(friend_id, days=28)
    stats_all    = compute_user_stats(friend_id, days=None)

    return render_template(
        'friends/friends_stats.html',
        username=User.query.get(friend_id).username,
        today_table=format_data(stats_today, 'table'),
        last7_table=format_data(stats_7days, 'table'),
        last28_table=format_data(stats_28days, 'table'),
        alltime_table=format_data(stats_all, 'table'),
        today_chart=format_data(stats_today, 'chart'),
        last7_chart=format_data(stats_7days, 'chart'),
        last28_chart=format_data(stats_28days, 'chart'),
        alltime_chart=format_data(stats_all, 'chart')
    )

@friends_bp.route('/friends/remove/<int:friend_id>', methods=['POST'])
@login_required
def remove_friend(friend_id):
    """
    Unfriend: delete both A→B and B→A rows.
    """
    # find both sides
    relationship1 = Friendship.query.get((current_user.user_id, friend_id))
    relationship2 = Friendship.query.get((friend_id, current_user.user_id))

    # if either side is missing or not “accepted”, error out
    if not relationship1 or not relationship2 or not relationship1.is_requested or not relationship2.is_requested:
        return jsonify(success=False, message="You're not currently friends."), 400

    # delete both
    db.session.delete(relationship1)
    db.session.delete(relationship2)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)

    # fallback for normal form
    flash('Friend removed.', 'info')
    return redirect(url_for('friends.friends'))

