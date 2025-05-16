import unittest
from app import create_app, db
from app.config import TestingConfig
from app.models import User, TypingResult, Paragraph, Friendship
from datetime import datetime
import sqlalchemy as sa
import json
from collections import Counter

class StatsBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
        
    def tearDown(self):
        # reset database
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    

    def helper_attempt_login(self):
        return self.client.post('/login', data={
            'username': "testuser",
            'password': "testpassword",
            'remember_me': True
        })
    
    def helper_create_user(self):
        with self.app.app_context():
            user_example = User(username='testuser', email='testuser@example.com', registration_time=datetime.now())
            user_example.set_password("testpassword")
            db.session.add(user_example)
            db.session.commit()
    
    def helper_create_paragraphs(self):
        with self.app.app_context():
            user: User = db.session.scalar(sa.select(User).where(User.username == "testuser")) 

            # Create a paragraph for the typing result
            paragraph_text = "The quick brown fox jumps over the lazy dog."
            paragraph = Paragraph(body=paragraph_text, type="normal")
            db.session.add(paragraph)
            db.session.commit()

            # Example correct and mistake lists
            correct_chars1 = dict(Counter(paragraph_text))
            correct_words1 = dict(Counter(paragraph_text))
            mistake_chars1 = dict(Counter(paragraph_text))
            mistake_words1 = dict(Counter(paragraph_text))

            correct_chars2 = dict(Counter(paragraph_text))
            correct_words2 = dict(Counter(paragraph_text))
            mistake_chars2 = dict(Counter(paragraph_text))
            mistake_words2 = dict(Counter(paragraph_text))

            # Example TypingResult entries
            result1 = TypingResult(
                user_id=user.user_id,
                paragraph_id=paragraph.paragraph_id,
                wpm=72,
                total_characters=len(correct_chars1),
                total_words=len(correct_words1),
                correct_characters=correct_chars1,
                correct_words=correct_words1,
                total_mistakes=len(mistake_chars1) + len(mistake_words1),
                mistake_characters=mistake_chars1,
                mistake_words=mistake_words1,
                timestamp=datetime.now()
            )
            result2 = TypingResult(
                user_id=user.user_id,
                paragraph_id=paragraph.paragraph_id,
                wpm=65,
                total_characters=len(correct_chars2),
                total_words=len(correct_words2),
                correct_characters=correct_chars2,
                correct_words=correct_words2,
                total_mistakes=len(mistake_chars2) + len(mistake_words2),
                mistake_characters=mistake_chars2,
                mistake_words=mistake_words2,
                timestamp=datetime.now()
            )
            db.session.add(result1)
            db.session.add(result2)

            db.session.commit()


    def test_page_loading(self):
        """Test that the stats page loads and contains expected content."""

        self.helper_create_user()

        response = self.helper_attempt_login()
        self.assertEqual(response.status_code, 302, "Could not log in.")

        response = self.client.get('/stats')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Stats_ID', response.data, "Did not properly load page.")


    def test_access_when_logged_in(self):
        """Test that the stats page does not load when you are not logged in."""

        response = self.client.get('/stats')
        self.assertNotEqual(response.status_code, 200, "Received code 200.")
        self.assertNotIn(b'Stats_ID', response.data, "Was able to access stats without logging in.")

    
    def test_access_friends_stats(self):
        """Test that a user can access their friend's stats page."""

        self.helper_create_user()
        self.helper_create_paragraphs()

        with self.app.app_context():
            # Create a second user
            friend = User(username='frienduser', email='friend@example.com', registration_time=datetime.now())
            friend.set_password('friendpassword')
            db.session.add(friend)

            user: User = db.session.scalar(sa.select(User).where(User.username == "testuser")) 
            friend:User= db.session.scalar(sa.select(User).where(User.username == "frienduser")) 

            # Create reciprocal Friendship entries (not requests)
            friendship1 = Friendship(user_id=user.user_id, friend_id=friend.user_id, is_requested=False, requesting_user=user.user_id)
            friendship2 = Friendship(user_id=friend.user_id, friend_id=user.user_id, is_requested=False, requesting_user=user.user_id)
            db.session.add(friendship1)
            db.session.add(friendship2)
            db.session.commit()

            # Log in as the main user
            response = self.helper_attempt_login()
            self.assertEqual(response.status_code, 302, "Could not log in.")

            # Access the friend's stats page
            response = self.client.get(f'/friends/{friend.username}/stats')
            self.assertEqual(response.status_code, 200, "Could not access friend's stats page.")
            self.assertIn(friend.username.encode(), response.data, "Friend's username not found in stats page.")
    

    