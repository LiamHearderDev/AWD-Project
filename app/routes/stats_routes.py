import random
import string
import json
from app import application
from flask import render_template, request, redirect, url_for, jsonify
from app.models import User

@application.route('/stats', methods=['GET'])
def stats():
    # 1) Table data
    today_stats = [
        {"metric": "Total Attempts", "value": 2, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average WPM", "value": 71.8, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average Accuracy", "value": "94.6%", "timestamp": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 74.2, "timestamp": "09:52 a.m. 05/03/2025", "paragraph": 1},
        {"metric": "Best Accuracy", "value": "95.8%", "timestamp": "09:52 a.m. 05/03/2025", "paragraph": 1},
        {"metric": "Least Mistakes in Words", "value": 4, "timestamp": "09:52 a.m. 05/03/2025", "paragraph": 1}
    ]

    last7days_stats = [
        {"metric": "Total Attempts", "value": 6, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average WPM", "value": 76.3, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average Accuracy", "value": "96.1%", "timestamp": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 82.5, "timestamp": "18:20 p.m. 04/30/2025", "paragraph": 3},
        {"metric": "Best Accuracy", "value": "97.3%", "timestamp": "18:20 p.m. 04/30/2025", "paragraph": 3},
        {"metric": "Least Mistakes in Words", "value": 2, "timestamp": "18:20 p.m. 04/30/2025", "paragraph": 3}
    ]

    last28days_stats = [
        {"metric": "Total Attempts", "value": 18, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average WPM", "value": 78.9, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average Accuracy", "value": "96.8%", "timestamp": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 86.7, "timestamp": "14:37 p.m. 04/12/2025", "paragraph": 5},
        {"metric": "Best Accuracy", "value": "98.1%", "timestamp": "14:37 p.m. 04/12/2025", "paragraph": 5},
        {"metric": "Least Mistakes in Words", "value": 1, "timestamp": "14:37 p.m. 04/12/2025", "paragraph": 5}
    ]

    alltime_stats = [
        {"metric": "Total Attempts", "value": 52, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average WPM", "value": 80.4, "timestamp": "-", "paragraph": "-"},
        {"metric": "Average Accuracy", "value": "97.2%", "timestamp": "-", "paragraph": "-"},
        {"metric": "Best WPM", "value": 91.3, "timestamp": "20:05 p.m. 03/21/2025", "paragraph": 4},
        {"metric": "Best Accuracy", "value": "99.0%", "timestamp": "20:05 p.m. 03/21/2025", "paragraph": 4},
        {"metric": "Least Mistakes in Words", "value": 0, "timestamp": "20:05 p.m. 03/21/2025", "paragraph": 4}
    ]

    # 2) Chart data arrays
    today_labels     = ["Attempt 1", "Attempt 2"]
    today_wpm        = [68.5, 74.2]
    today_accuracy   = [93.2, 95.8]

    last7_labels     = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    last7_wpm        = [72, 74, 78, 76, 79, 75, 80]
    last7_accuracy   = [94, 95, 96, 95, 97, 94, 96]

    last28_labels    = ["Week 1","Week 2","Week 3","Week 4"]
    last28_wpm       = [73, 76, 79, 86.7]
    last28_accuracy  = [95.9, 96.3, 97.0, 98.1]

    all_labels       = ["Mar","Apr","May"]
    all_wpm          = [75.5, 80.2, 91.3]
    all_accuracy     = [96.5, 97.4, 99.0]

    return render_template(
        'stats/stats.html',
        today=today_stats,
        last7days=last7days_stats,
        last28days=last28days_stats,
        alltime=alltime_stats,
        # chart context:
        today_labels=today_labels,
        today_wpm=today_wpm,
        today_accuracy=today_accuracy,
        last7_labels=last7_labels,
        last7_wpm=last7_wpm,
        last7_accuracy=last7_accuracy,
        last28_labels=last28_labels,
        last28_wpm=last28_wpm,
        last28_accuracy=last28_accuracy,
        all_labels=all_labels,
        all_wpm=all_wpm,
        all_accuracy=all_accuracy
    )

shared_data = {}
#  Generate a random string for generation of the url in the syntax of '/stats/shared_stats/<userid>/<random_str>'
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

