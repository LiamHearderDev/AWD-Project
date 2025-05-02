from app import db, application
from app.models import Paragraph, TypingResult
import json

def add_paragraph(body, type=None): # add a new paragraph to the database
    if not body or not body.strip():
        raise ValueError("Paragraph body cannot be empty")

    new_paragraph = Paragraph(body=body.strip(), type=type)
    db.session.add(new_paragraph)
    db.session.commit()
    return new_paragraph

def display_results_for_user(user_id): # display all results for a specific user
    results = TypingResult.query.filter_by(user_id=user_id).all()

    if not results:
        print(f"No results found for user ID {user_id}")
        return

    for r in results:
        print(f"Result ID: {r.result_id}")
        print(f"Paragraph ID: {r.paragraph_id}")
        print(f"WPM: {r.wpm}")
        print(f"Total Characters: {r.total_characters}")
        print(f"Correct Characters: {json.loads(r.correct_characters)}")
        print(f"Total Words: {r.total_words}")
        print(f"Correct Words: {json.loads(r.correct_words)}")
        print(f"Total Mistakes: {r.total_mistakes}")
        print(f"Mistake Characters: {json.loads(r.mistake_characters)}")
        print(f"Timestamp: {r.timestamp}")
        print("-" * 40)


def purge_result_table():
    if __name__ == "__main__":
        with application.app_context():
            num_deleted = db.session.query(TypingResult).delete()
            db.session.commit()
            print(f"Deleted {num_deleted} rows from result table.")


if __name__ == "__main__":
    with application.app_context():
        # functions go here
        # add_paragraph("This is a test paragraph.", "normal")
        # purge_result_table()
        # display_results_for_user(1)
