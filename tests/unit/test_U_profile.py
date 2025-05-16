import unittest
import os
import sys

from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app, db
from app.models import User
from app.config import TestingConfig

class ProfilePageTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        #self.app.config['MAIL_DEFAULT_SENDER'] = 'sender@gmail.com'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            user = User(username='bingocat', email='bingocat@gmail.com', registration_time=datetime.now())
            user.set_password('bingocat123')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.user_id
        

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_test_user(self):
        with self.client:
            self.client.post('/login', data={
                'username': 'bingocat',
                'password': 'bingocat123',
                'remember_me': True
            })

    def test_profile_page_loads(self):
        self.login_test_user()
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Profile', response.data)

    def test_update_profile_username(self):
        self.login_test_user()
        response = self.client.post('/profile', data={
            'username': 'newname',
            'password': '',
            'confirm_password': '',
            'submit': True
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your profile has been updated successfully', response.data)
        with self.app.app_context():
            user = User.query.filter_by(user_id=self.user_id).first()
            self.assertEqual(user.username, 'newname')

    def test_update_profile_password_mismatch(self):
        self.login_test_user()
        response = self.client.post('/profile', data={
            'username': '',
            'password': 'newpassword',
            'confirm_password': 'different',
            'submit': True
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords must match', response.data)

if __name__ == '__main__':
    unittest.main()