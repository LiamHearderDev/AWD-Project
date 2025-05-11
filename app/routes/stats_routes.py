import json
import random
import string
from datetime import datetime, timedelta

from flask import render_template, request, url_for, jsonify, flash, abort, Blueprint
from flask_login import login_required, current_user
from sqlalchemy import func

from app import application, db
from app.models import TypingResult, User, Friendship

import ast      # This allows us to convert string literals into their respective types, like dictionaries.


stats_bp = Blueprint('stats', __name__)

def compute_user_stats(user_id: int | None, days: int = None) -> dict:

    # If user_id is None, stats are for current_user; otherwise for that ID
    """
    This function calculates key statistics for a user over a given time window. To be used within `stats.html`, the output must first go through the function `format_data()`.
    Parameters:
        days (int): An integer that determines how long ago each TypingResult is allowed to be. Anything outside of this range is not included in the result. A value of None will allow all results.
    Returns:
      user_stats (dict): A dict with total_attempts, average words per minute, best words per minute, all words per minute results, avg accuracy, best accuracy, and all accuracy results.
    """

    # This ensures that days is not negative. If it is negative, make it None.
    days = days if days is None or days >= 0 else None
    uid  = user_id if user_id is not None else current_user.user_id

  # Base query for the specified user
    query = TypingResult.query.filter(TypingResult.user_id == uid)
    if days is not None :
        # since = datetime.utcnow() - timedelta(days=days)
        since = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) if days==0 else datetime.now()-timedelta(days=days)
        query = query.filter(TypingResult.timestamp >= since)

    # Fetch all matching results
    results = query.all()
    if len(results) == 0:
        return {
            "total_attempts": 0,
            "avg_wpm": 0.0,
            "best_wpm": 0.0,
            "best_wpm_timestamp" : None,
            "best_wpm_paragraph": None,
            "all_wpm": [],
            "avg_accuracy": "0.0%",
            "best_accuracy": "0.0%",
            "best_accuracy_timestamp": None,
            "best_accuracy_paragraph": None,
            "all_accuracy": [],
            "result_timestamps": []
        }

    # This is to be used when needing to flash an error to the screen in the following loop
    def flash_error(field: str, id: int):
        flash(f'An unexpected error occurred. Could not parse data for field [{field}]. Corrupted data found at TypingResult id: {id}')
        return

    # Compute data for each result
    acc_values: list = []
    best_acc: int = 0
    best_acc_timestamp: datetime = None
    best_acc_paragraph: int = None
    wpms: list = []
    result_timestamps: list = []
    best_wpm: int = 0
    best_wpm_timestamp: datetime = None
    best_wpm_paragraph: int = None


    # Loop over every TypingResult
    for result in results:
        correct = ast.literal_eval(result.correct_characters) # Need to convert to a dict by eval string literal

        # Check for any issues
        if not isinstance(correct, dict):
            flash_error("correct_characters", result.result_id)
            continue
        if result.total_characters <= 0:
            flash_error("total_characters", result.result_id)
            continue
        if result.wpm < 0:
            flash_error("wpm", result.result_id)
            continue
        
        # Cache data
        result_timestamps.append(result.timestamp.strftime("%H:%M, %d/%m/%Y"))
        correct_count = sum(correct.values())
        this_acc = (correct_count / result.total_characters) * 100

        acc_values.append(this_acc)
        if this_acc >= best_acc:
            best_acc = this_acc
            best_acc_timestamp = result.timestamp.strftime("%H:%M, %d/%m/%Y")
            best_acc_paragraph = result.paragraph_id

        wpms.append(result.wpm)
        if result.wpm >= best_wpm:
            best_wpm = result.wpm
            best_wpm_timestamp = result.timestamp.strftime("%H:%M, %d/%m/%Y")
            best_wpm_paragraph = result.paragraph_id
        
    if len(acc_values) <= 0:
        avg_acc = 0.0
        best_acc = 0.0
    else:
        avg_acc = sum(acc_values) / len(acc_values)
        best_acc = max(acc_values)

    avg_wpm = sum(wpms) / len(results)

    return {
        "total_attempts": len(results),
        "avg_wpm": round(avg_wpm, 1),
        "best_wpm": round(best_wpm, 1),
        "best_wpm_timestamp": best_wpm_timestamp,
        "best_wpm_paragraph": best_wpm_paragraph,
        "all_wpm": wpms,
        "avg_accuracy": f"{round(avg_acc, 1)}%",
        "best_accuracy": f"{round(best_acc, 1)}%",
        "best_accuracy_timestamp": best_acc_timestamp,
        "best_accuracy_paragraph": best_acc_paragraph,
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
                {"metric": "Best WPM",             "value": stats_dict["best_wpm"],         "timestamp": stats_dict["best_wpm_timestamp"] if stats_dict["best_wpm_timestamp"] != None else "-",             "paragraph": stats_dict["best_wpm_paragraph"] if stats_dict["best_wpm_paragraph"] != None else "-"},
                {"metric": "Best Accuracy",        "value": stats_dict["best_accuracy"],    "timestamp": stats_dict["best_accuracy_timestamp"] if stats_dict["best_accuracy_timestamp"] != None else "-",   "paragraph": stats_dict["best_accuracy_paragraph"] if stats_dict["best_accuracy_paragraph"] != None else "-"}
            ]
        case "chart":
            return {
                "labels":   stats_dict["result_timestamps"],
                "wpm":      stats_dict["all_wpm"],
                "accuracy": stats_dict["all_accuracy"]
            }
        case _:
            return None



@stats_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    """User stats dashboard."""

    #Compute stats per period   
    uid = current_user.user_id
    stats_today  = compute_user_stats(uid, days=0)
    stats_7days  = compute_user_stats(uid, days=7)
    stats_28days = compute_user_stats(uid, days=28)
    stats_all    = compute_user_stats(uid, days=None)

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

@stats_bp.route('/friends_stats/<int:friend_id>')
@login_required
def friends_stats(friend_id):
    """
    Shows stats for a friend at /friends_stats/<friend_id>.
    """
    # 1) Verify they’re actually your friend
    rel = Friendship.query.get((current_user.user_id, friend_id))
    if not rel or not rel.is_requested:
        abort(403)

    # 2) Compute exactly as in your /stats route
    uid = friend_id
    stats_today  = compute_user_stats(uid, days=0)
    stats_7days  = compute_user_stats(uid, days=7)
    stats_28days = compute_user_stats(uid, days=28)
    stats_all    = compute_user_stats(uid, days=None)

    # 3) Render a special template
    return render_template(
        'friends/friends_stats.html',
        username=User.query.get(uid).username,
        today_table      = format_data(stats_today,  'table'),
        last7_table      = format_data(stats_7days,  'table'),
        last28_table     = format_data(stats_28days, 'table'),
        alltime_table    = format_data(stats_all,     'table'),
        today_chart      = format_data(stats_today,   'chart'),
        last7_chart      = format_data(stats_7days,   'chart'),
        last28_chart     = format_data(stats_28days,  'chart'),
        alltime_chart    = format_data(stats_all,     'chart')
    )

@stats_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template('stats/leaderboard.html')

@stats_bp.route('/api/leaderboard')
def get_leaderboard():
    top_users = User.query.order_by(User.highest_wpm.desc()).limit(10).all()

    data = {
        'username': [user.username for user in top_users],
        'wpm': [user.highest_wpm for user in top_users]
    }
    return jsonify(data)

