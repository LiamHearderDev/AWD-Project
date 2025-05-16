from app import db
from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, TypingResult, Friendship
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app.forms import UpdateProfileForm
from flask_mail import Message
from app.extensions import mail

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # Handle main logic here
    return render_template('main/dashboard.html')

@main_bp.route('/profile', defaults={'user_id': None}, methods=['GET','POST']) #give it a default user_id
@main_bp.route('/profile/<int:user_id>', methods=['GET','POST'])
@login_required
def profile(user_id):
    # 1) look up the user (404 if missing)
    if user_id is None:
        user = current_user
    else:
        user = User.query.get_or_404(user_id)

    # 2) compute exactly the same stats, but for `user.user_id` instead of current_user
    uid = user.user_id

    # NEED:
    """
    WPM,
    Friend count,
    Account age,
    Rank
    """

    wpm             : int = 0
    friends_count   : int = 0
    account_age     : str = ""
    rank            : int = 0
    max_rank        : int = 0


    ##### Calculate Average WPM #####

    # This will query every TypingResult, getting only this user's, then average them all out.
    wpm = db.session.query(func.avg(TypingResult.wpm)).filter(TypingResult.user_id == uid).scalar()

    ##### Calculate Friends Count #####

    friends_query = Friendship.query.filter(Friendship.user_id == uid)
    friends_result = friends_query.all()
    friends_count = len(friends_result)


    ##### Calculate Account Age #####

    account_delta = datetime.now() - user.registration_time
    if account_delta.days < 28:
        account_age = f"{account_delta.days} days" if account_delta.days != 1 else f"{account_delta.days} day"
    elif account_delta.days < 365:
        account_age = f"{account_delta.days // 30} months" if account_delta.days // 30 != 1 else f"{account_delta.days // 30} month"
    else:
        account_age = f"{account_delta.days // 365} years" if account_delta.days // 365 != 1 else f"{account_delta.days // 365} year"
    

    ##### Calculate Account Rank #####

    # This creates a new table (via a subquery) with the fields "rank" and "user_id" by sorting the list of users in SQL.
    leaderboard_query = db.session.query( 
        func.rank().over(order_by=User.highest_wpm.desc()).label('rank'),
        User.user_id
    ).subquery()
    
    # This filters the new table for the current user and checks, then stores, the rank field.
    rank = db.session.query(leaderboard_query.c.rank).filter(leaderboard_query.c.user_id == uid).scalar()
    max_rank = db.session.query(func.count(User.user_id)).scalar()

    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.username.data:
            existing = User.query.filter_by(username=form.username.data).first()
            if existing and existing.user_id != current_user.user_id:
                flash('Username already exists. Please choose a different one!')
                # re‐render the same page with the full context
                return render_template(
                    'main/profile.html',
                    user=current_user,
                    wpm=wpm,
                    friends_count=friends_count,
                    account_age=account_age,
                    rank=rank,
                    max_rank=max_rank,
                    form=form,
                )

            current_user.username = form.username.data

        if form.password.data:
            current_user.set_password(form.password.data)
        
        db.session.commit()
        msg = Message(
            subject='Your SpeedLogger profile has been updated',
            recipients=[current_user.email],
            body=f"Hello {current_user.username},\n\nYour profile has been updated successfully.\n\nIf you did not make this change, please contact support."
        )
        mail.send(msg)
        flash('Your profile has been updated successfully!')
        return redirect(url_for('main.profile'))
    
    return render_template('main/profile.html', 
        user            =   user,
        wpm             =   wpm, 
        friends_count   =   friends_count, 
        account_age     =   account_age, 
        rank            =   rank, 
        max_rank        =   max_rank,
        form            =   form
    )
