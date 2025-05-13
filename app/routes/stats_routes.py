import json
import random
import string
from datetime import datetime, timedelta

from flask import render_template, request, url_for, jsonify, flash, Blueprint
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import TypingResult, User

import ast      # This allows us to convert string literals into their respective types, like dictionaries.

from collections import Counter  # This allows us to do some statistics on the data


stats_bp = Blueprint('stats', __name__)


def compute_user_stats(user_id: int | None = None, days: int = None) -> dict:

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
    print(f"[DEBUG] Days={days}, Found results: {len(results)}")
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
            "result_timestamps": [],
            "most_incorrect_words": []
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

    mistake_words_counter = Counter()
    mistake_words_values: list = []

    # Loop over every TypingResult
    for result in results:
        correct = ast.literal_eval(result.correct_characters) # Need to convert to a dict by eval string literal
        mistake_words = ast.literal_eval(result.mistake_words) 

        # Check for any issues
        if not isinstance(correct, dict):
            flash_error("correct_characters", result.result_id)
            continue
        if not isinstance(mistake_words, dict):
            flash_error("mistake_words", result.result_id)
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

        if result.mistake_words:
            mistake_words_counter.update(mistake_words)

    most_incorrect_words = mistake_words_counter.most_common(8)
    mistake_words_labels = [word for word, count in most_incorrect_words]
    mistake_words_counts = [count for word, count in most_incorrect_words]
 

        
        
        
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
        "result_timestamps": result_timestamps,
        "most_incorrect_words_labels": mistake_words_labels,
        "most_incorrect_words_counts": mistake_words_counts,

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
        alltime_chart       = format_data(stats_all,   "chart"),

        # Words leaderboard data
        today_typing_labels = stats_today["most_incorrect_words_labels"],
        today_typing_counts = stats_today["most_incorrect_words_counts"],
        last7days_typing_labels = stats_7days["most_incorrect_words_labels"],
        last7days_typing_counts = stats_7days["most_incorrect_words_counts"],
        last28days_typing_labels = stats_28days["most_incorrect_words_labels"],
        last28days_typing_counts = stats_28days["most_incorrect_words_counts"],
        alltime_typing_labels = stats_all["most_incorrect_words_labels"],
        alltime_typing_counts = stats_all["most_incorrect_words_counts"],
    )



shared_data = {}
#  Generate a random string for generation of the url in the syntax of '/stats/shared_stats/<userid>/<random_str>'
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@stats_bp.route('/stats/shared_stats/<userid>/<random_str>', methods=['GET'])
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

@stats_bp.route('/stats/generate_report', methods=['POST'])
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

    return jsonify({"url": url_for('stats.shared_stats', userid=userid, random_str=random_str)})

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
