import json
import random
import string
from datetime import datetime, timedelta

from flask import render_template, request, url_for, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from app import application, db
from app.models import TypingResult, User

import ast      # This allows us to convert string literals into their respective types, like dictionaries.




def compute_user_stats(days: int = None) -> dict:
    """
    This function calculates key statistics for a user over a given time window. To be used within `stats.html`, the output must first go through the function `format_data()`.
    Parameters:
        days (int): An integer that determines how long ago each TypingResult is allowed to be. Anything outside of this range is not included in the result. A value of None will allow all results.
    Returns:
      user_stats (dict): A dict with total_attempts, average words per minute, best words per minute, all words per minute results, avg accuracy, best accuracy, and all accuracy results.
    """

    # This ensures that days is not negative. If it is negative, make it None.
    days = days if days == None or days >= 0 else None

    # Base query for this user
    query = TypingResult.query.filter(TypingResult.user_id == current_user.user_id)
    if days is not None :
        # since = datetime.utcnow() - timedelta(days=days)
        since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) if days==0 else datetime.now()-timedelta(days=days)
        query = query.filter(TypingResult.timestamp >= since)

    # Fetch all matching results
    results = query.all()
    total = len(results)
    if total == 0:
        return {
            "total_attempts": 0,
            "avg_wpm": 0.0,
            "best_wpm": 0.0,
            "all_wpm": [],
            "avg_acc": "0.0%",
            "best_acc": "0.0%",
            "all_accuracy": [],
            "result_timestamps": []
        }

    # Compute WPM stats
    wpms = [r.wpm for r in results]
    result_timestamps = [r.timestamp.strftime("%b %d %H:%M") for r in results]
    avg_wpm = sum(wpms) / total
    best_wpm = max(wpms)

    # Compute accuracy per result (percentage)
    acc_values = []
    for r in results:
        correct = ast.literal_eval(r.correct_characters) # Need to convert to a dict by eval string literal
        if isinstance(correct, dict):
            correct_count = sum(correct.values())
        else:
            flash("Could not correctly parse data for [TypingResult.correct_characters]. Corrupted data found at TypingResult id: " + r.result_id)
            continue
        if r.total_characters > 0:
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
        "all_wpm": wpms,
        "avg_accuracy": f"{round(avg_acc, 1)}%",
        "best_accuracy": f"{round(best_acc, 1)}%",
        "all_accuracy": acc_values,
        "result_timestamps": result_timestamps
    }


def format_data(stats_dict: dict, format: str):
    """
    This function converts the input dictionary into a format suitable for the table or chart.
    Parameters:
        stats_dict      (dict): This is a dictionary of user statistics. This should always be the output of the function `compute_user_stats()`.
        format          (str):  A string representing the format which the function should output. Should be either `"table"` or `"chart"`. Anything else will cause this function to output a value of `None`.
    Returns:
        formatted_data  (dict / list):     Depending on the value of the parameter `format`, this function either returns a list of dictionaries suitable for tables, or a dictionary suitable for charts. If `format` is incorrectly set, the output will be `None`.
    """

    match format:
        case "table":
            return [
                {"metric": "Total Attempts",       "value": stats_dict["total_attempts"],   "timestamp": "-", "paragraph": "-"},
                {"metric": "Average WPM",          "value": stats_dict["avg_wpm"],          "timestamp": "-", "paragraph": "-"},
                {"metric": "Average Accuracy",     "value": stats_dict["avg_accuracy"],     "timestamp": "-", "paragraph": "-"},
                {"metric": "Best WPM",             "value": stats_dict["best_wpm"],         "timestamp": "-", "paragraph": "-"},
                {"metric": "Best Accuracy",        "value": stats_dict["best_accuracy"],    "timestamp": "-", "paragraph": "-"}
            ]
        case "chart":
            return {
                "labels":   stats_dict["result_timestamps"],
                "wpm":      stats_dict["all_wpm"],
                "accuracy": stats_dict["all_accuracy"]
            }
        case _:
            return None



@application.route('/stats', methods=['GET'])
@login_required
def stats():
    """User stats dashboard."""

    # Compute stats per period
    stats_today     = compute_user_stats(days=0)
    stats_7days     = compute_user_stats(days=7)
    stats_28days    = compute_user_stats(days=28)
    stats_all       = compute_user_stats(days=None)

    # Render template with dynamic data
    return render_template('stats/stats.html',
                           
        # Table data
        today_table         = format_data(stats_today, "table"),
        last7days_table     = format_data(stats_7days, "table"),
        last28days_table    = format_data(stats_28days,"table"),
        alltime_table       = format_data(stats_all,   "table"),

        # Chart data
        today_chart         = format_data(stats_today, "chart"),
        last7days_chart     = format_data(stats_7days, "chart"),
        last28days_chart    = format_data(stats_28days,"chart"),
        alltime_chart       = format_data(stats_all,   "chart")
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
    return render_template('stats/leaderboard.html')

@application.route('/api/leaderboard')
def get_leaderboard():
    top_users = User.query.order_by(User.highest_wpm.desc()).limit(10).all()

    data = {
        'username': [user.username for user in top_users],
        'wpm': [user.highest_wpm for user in top_users]
    }
    return jsonify(data)
