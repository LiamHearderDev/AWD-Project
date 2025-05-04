import json
import random
import string
from datetime import datetime, timedelta

from flask import render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app import application, db
from app.models import TypingResult, User




def compute_user_stats(user_id, days: int = None):
    """
    Calculate key statistics for a user over the given time window.

    Returns:
      A dict with total_attempts, avg_wpm, best_wpm, avg_acc, best_acc
    """
    # Base query for this user
    q = TypingResult.query.filter(TypingResult.user_id == user_id)
    if days is not None :
        # since = datetime.utcnow() - timedelta(days=days)
        since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) if days==0 else datetime.utcnow()-timedelta(days=days)
        q = q.filter(TypingResult.timestamp >= since)

    # Fetch all matching results
    results = q.all()
    total = len(results)
    if total == 0:
        return {
            "total_attempts": 0,
            "avg_wpm": 0.0,
            "best_wpm": 0.0,
            "avg_acc": "0.0%",
            "best_acc": "0.0%"
        }

    # Compute WPM stats
    wpms = [r.wpm for r in results]
    avg_wpm = sum(wpms) / total
    best_wpm = max(wpms)

    # Compute accuracy per result (percentage)
    acc_values = []
    for r in results:
        correct = r.correct_characters  # already a Python list or dict
        if isinstance(correct, dict):
            correct_count = sum(correct.values())
        else:
            correct_count = len(correct)
        if r.total_characters:
            acc_values.append((correct_count / r.total_characters) * 100)
    if not acc_values:
        avg_acc = best_acc = 0.0
    else:
        avg_acc = sum(acc_values) / len(acc_values)
        best_acc = max(acc_values)

    return {
        "total_attempts": total,
        "avg_wpm": round(avg_wpm, 1),
        "best_wpm": round(best_wpm, 1),
        "avg_acc": f"{round(avg_acc, 1)}%",
        "best_acc": f"{round(best_acc, 1)}%"
    }


def make_row_list(stats_dict):
    """
    Convert the stats dictionary into a list of row dicts for the template.
    """
    return [
        {"metric": "Total Attempts",       "value": stats_dict["total_attempts"], "timestamp": "-", "paragraph": "-"},
        {"metric": "Average WPM",          "value": stats_dict["avg_wpm"],       "timestamp": "-", "paragraph": "-"},
        {"metric": "Average Accuracy",     "value": stats_dict["avg_acc"],       "timestamp": "-", "paragraph": "-"},
        {"metric": "Best WPM",             "value": stats_dict["best_wpm"],      "timestamp": "-", "paragraph": "-"},
        {"metric": "Best Accuracy",        "value": stats_dict["best_acc"],      "timestamp": "-", "paragraph": "-"}
    ]

def get_series(user_id, days=None):
    """
    CHANGED: Build Chart.js series from DB rows for the given period.
    Returns labels, wpm_list, accuracy_list.
    """
    q = TypingResult.query.filter(TypingResult.user_id == user_id)
    if days is not None and days > 0:
        since = datetime.utcnow() - timedelta(days=days)
        q = q.filter(TypingResult.timestamp >= since)
    rows = q.order_by(TypingResult.timestamp).all()

    labels = [r.timestamp.strftime("%b %d %H:%M") for r in rows]
    wpms = [r.wpm for r in rows]
    accs = []
    for r in rows:
        correct = r.correct_characters
        if isinstance(correct, dict):
            correct_count = sum(correct.values())
        else:
            correct_count = len(correct)
        if r.total_characters:
            accs.append((correct_count / r.total_characters) * 100)
    return labels, wpms, accs

@application.route('/stats', methods=['GET'])
@login_required
def stats():
    """User stats dashboard."""
    uid = current_user.user_id
    uname    = current_user.username

    # Calculate cutoffs
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    since7  = now - timedelta(days=7)
    since28 = now - timedelta(days=28)

    # Compute stats per period
    # stats_today  = compute_user_stats(uid, days=None if False else today_start)
    stats_today = compute_user_stats(uid, days=0)
    stats_7days  = compute_user_stats(uid, days=7)
    stats_28days = compute_user_stats(uid, days=28)
    stats_all    = compute_user_stats(uid, days=None)

    # Prepare chart series per period
    labels_today,  wp_today,  acc_today  = get_series(uid, days=None)
    labels_7,      wp_7,      acc_7      = get_series(uid, days=7)
    labels_28,     wp_28,     acc_28     = get_series(uid, days=28)
    labels_all,    wp_all,    acc_all    = get_series(uid, days=None)

    # Render template with dynamic data
    return render_template('stats/stats.html',
        user_id       = uid,                  # CHANGED
        username      = uname,                # CHANGED
        today         = make_row_list(stats_today),
        last7days     = make_row_list(stats_7days),
        last28days    = make_row_list(stats_28days),
        alltime       = make_row_list(stats_all),

        today_labels    = labels_today,
        today_wpm       = wp_today,
        today_accuracy  = acc_today,

        last7_labels    = labels_7,
        last7_wpm       = wp_7,
        last7_accuracy  = acc_7,

        last28_labels   = labels_28,
        last28_wpm      = wp_28,
        last28_accuracy = acc_28,

        all_labels      = labels_all,
        all_wpm         = wp_all,
        all_accuracy    = acc_all
    )

shared_data = {}
#  Generate a random string for generation of the url in the syntax of '/stats/shared_stats/<userid>/<random_str>'
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@application.route('/stats/shared_stats/<userid>/<random_str>', methods=['GET'])
def shared_stats(userid, random_str):
    key = userid + random_str
    data = shared_data.get(key, {})
    # lookup the sharing user:
    user = User.query.get_or_404(int(userid))
    return render_template('stats/shared_stats.html',
        data=data,
        user_id=user.user_id,
        username=user.username
    )

@application.route('/stats/generate_report', methods=['POST'])
def generate_report():
    userid = request.form['userid']
    period = request.form['period']
    data = json.loads(request.form['data'])

    random_str = generate_random_string()
    key = userid + random_str
    shared_data[key] = {
        "period": period,
        "stats": data["stats"],
        "labels": data["labels"],
        "wpm": data["wpm"],
        "accuracy": data["accuracy"]
    }

    return jsonify({"url": url_for('shared_stats', userid=userid, random_str=random_str)})

@application.route('/leaderboard', methods=['GET'])
def leaderboard():
    #top_users = User.query.order_by(User.highest_wpm.desc()).limit(10).all()
    return render_template('stats/leaderboard.html')

@application.route('/api/leaderboard')
def get_leaderboard():
    top_users = User.query.order_by(User.highest_wpm.desc()).limit(10).all()

    data = {
        'username': [user.username for user in top_users],
        'wpm': [user.highest_wpm for user in top_users]
    }
    return jsonify(data)
