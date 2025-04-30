import random
import string
import json
from app import application
from flask import render_template, request, redirect, url_for, jsonify

@application.route('/stats', methods=['GET'])
def stats():
    # Data for different time periods
    today_stats = [
        {"metric": "Total Attempts", "value": 1, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
        {"metric": "Best WPM", "value": 75.3, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
        {"metric": "Best Accuracy", "value": "95.2%", "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
        {"metric": "Best Word Count", "value": 310, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
        {"metric": "Best Correct Words Count", "value": 295, "time": "10:15 a.m. 04/25/2025", "paragraph": 2},
        {"metric": "Least Mistakes in Words", "value": 5, "time": "10:15 a.m. 04/25/2025", "paragraph": 2}
    ]

    last7days_stats = [
        {"metric": "Total Attempts", "value": 5, "time": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 78.5, "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
        {"metric": "Best Accuracy", "value": "96.4%", "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
        {"metric": "Best Word Count", "value": 325, "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
        {"metric": "Best Correct Words Count", "value": 312, "time": "23:14 p.m. 04/15/2025", "paragraph": 3},
        {"metric": "Least Mistakes in Words", "value": 3, "time": "23:14 p.m. 04/15/2025", "paragraph": 3}
    ]

    last28days_stats = [
        {"metric": "Total Attempts", "value": 12, "time": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 84.2, "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
        {"metric": "Best Accuracy", "value": "97.1%", "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
        {"metric": "Best Word Count", "value": 355, "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
        {"metric": "Best Correct Words Count", "value": 345, "time": "19:02 p.m. 04/05/2025", "paragraph": 4},
        {"metric": "Least Mistakes in Words", "value": 2, "time": "19:02 p.m. 04/05/2025", "paragraph": 4}
    ]

    alltime_stats = [
        {"metric": "Total Attempts", "value": 37, "time": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 88.9, "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
        {"metric": "Best Accuracy", "value": "98.5%", "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
        {"metric": "Best Word Count", "value": 382, "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
        {"metric": "Best Correct Words Count", "value": 377, "time": "15:45 p.m. 03/10/2025", "paragraph": 2},
        {"metric": "Least Mistakes in Words", "value": 1, "time": "15:45 p.m. 03/10/2025", "paragraph": 2}
    ]

    return render_template('stats/stats.html',
                           today=today_stats,
                           last7days=last7days_stats,
                           last28days=last28days_stats,
                           alltime=alltime_stats)

shared_data = {}

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@application.route('/stats/shared_stats/<userid>/<random_str>', methods=['GET'])
def shared_stats(userid, random_str):
    key = userid + random_str
    data = shared_data.get(key, {})
    return render_template('stats/shared_stats.html', data=data)


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

@application.route('/stats/all_attempts', methods=['GET'])
def all_attempts():
    return render_template('stats/all_attempts.html')

@application.route('/leaderboard', methods=['GET'])
def leaderboard():
    return render_template('stats/leaderboard.html')
