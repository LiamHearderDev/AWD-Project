from app import db, application
from app.models import User, TypingResult
from datetime import datetime

import random

# Add test users to the User table with random values
def create_test_users():
    # clear existing user
    User.query.delete()
    db.session.commit()
    users = [
        {"username": "U1", "email": "u1@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "U2", "email": "u2@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "BlackCat", "email": "u3@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "U4", "email": "u4@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "U5", "email": "u5@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "Ginger", "email": "u6@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "U7", "email": "u7@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "U8", "email": "u8@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "CowCat", "email": "u9@gmail.com", "highest_wpm": random.randint(50,150)},
        {"username": "U10", "email": "u10@gmail.com", "highest_wpm": random.randint(50,150)},
    ]

    for user_data in users:
        user = User(
            username = user_data["username"],
            email=user_data["email"],
            password="blablabla",
            registration_time=datetime.utcnow(),
            highest_wpm = user_data["highest_wpm"]
        )
        db.session.add(user)
    db.session.commit()
    print("Users created!")


def create_test_typing_results():
    users = User.query.all()
    for user in users:
        for _ in range(5):  # Add 5 typing results per user
            result = TypingResult(
                user_id=user.user_id,
                paragraph_id=random.randint(1, 10),  # Assuming you have paragraphs with IDs 1-10
                wpm=random.randint(50, 120),
                total_characters=random.randint(200, 500),
                correct_characters={"a": random.randint(0, 10), "b": random.randint(0, 10)}, 
                total_words=random.randint(40, 100),
                correct_words=random.randint(10,100),
                total_mistakes=random.randint(0, 10),
                mistake_characters={"a": random.randint(0, 10), "b": random.randint(0, 10)}, 
                
                timestamp=datetime.utcnow()
            )
            db.session.add(result)
    db.session.commit()
    print("test typing result creted!")


    all_users = User.query.all()
    print("All users in the database:")
    # for user in all_users:
    #     print(user.username, user.highest_wpm)


if __name__ == "__main__":
    with application.app_context():
        create_test_users()
        create_test_typing_results()