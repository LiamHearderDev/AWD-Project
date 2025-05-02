from app import db
from app.models import Paragraph

def add_paragraph(body, type=None): # add a new paragraph to the database
    if not body or not body.strip():
        raise ValueError("Paragraph body cannot be empty")

    new_paragraph = Paragraph(body=body.strip(), type=type)
    db.session.add(new_paragraph)
    db.session.commit()
    return new_paragraph