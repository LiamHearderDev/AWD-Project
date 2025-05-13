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
    """
    GET: display the friend-request form, incoming requests, and friends list
    POST: handle new friend request (returns JSON for AJAX calls)
    """
    form = FriendRequestForm()

    # handle AJAX send-request
    if form.validate_on_submit():
        target_id = form.user_id.data
        # look up by ID
        target = User.query.get(target_id)

        # error if no such user or they try to add themselves
        if not target or target.user_id == current_user.user_id:
            return jsonify(
                success=False,
                message=f'User with ID {target_id} not found.'
            )

        # cross-request check: if the target already sent you a pending request
        incoming_req = Friendship.query.get((target_id, current_user.user_id))
        if incoming_req and incoming_req.is_requested is False:
            return jsonify(
                success=False,
                message='The target user has already sent you a request.'
            )

        # prevent duplicate outgoing or already-friends
        existing = Friendship.query.get((current_user.user_id, target_id))
        if existing:
            return jsonify(
                success=False,
                message="Request already sent or you're already friends."
            )

        # create the pending row
        friend_request = Friendship(
            user_id=current_user.user_id,
            friend_id=target_id,
            is_requested=False,
            requesting_user=current_user.user_id
        )
        db.session.add(friend_request)
        db.session.commit()
        return jsonify(success=True)

    # GET: load lists
    incoming   = Friendship.query.filter_by(
        friend_id=current_user.user_id,
        is_requested=False
    ).all()
    my_friends = Friendship.query.filter_by(
        user_id=current_user.user_id,
        is_requested=True
    ).all()

    return render_template(
        'friends/friends.html',
        form=form,
        incoming=incoming,
        my_friends=my_friends
    )

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
        ## By checking == 'XMLHttpRequest', your server knows “this came from JS, not a direct browser navigation or form submit
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
