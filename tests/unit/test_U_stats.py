import unittest
from app import create_app, db
from app.config import TestingConfig
from app.models import User, TypingResult, Paragraph

class StatsBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['LOGIN_DISABLED'] = True # make it so that @login_required in routes can accept from anonymous (for testing)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
        
    def tearDown(self):
        # reset database
        with self.app.app_context():
            db.session.remove()
            db.drop_all()