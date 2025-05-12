import unittest
from app import create_app, db
from app.config import TestingConfig

class GameBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        # create app with test config and context
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # reset database
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    

if __name__ == '__main__':
    unittest.main()
