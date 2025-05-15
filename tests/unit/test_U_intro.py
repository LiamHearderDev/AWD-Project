import unittest
from app import create_app, db
from app.config import TestingConfig

class IntroBluePrintTestCase(unittest.TestCase):
    def setUp(self):
        # create app with config 
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_intro_page_load(self):
        """ Make sure the intro page load successfully with expected content """
        response = self.client.get('/intro')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Track your typing performance and compete with friends!', response.data)
        self.assertIn(b'Start Playing', response.data)
        self.assertIn(b'Key Features', response.data)
        self.assertIn(b'About', response.data)

    def test_start_playing_button(self):
        """ Make sure the start playing button redirects to the game page """
        response = self.client.get('/intro')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/game"', response.data)
        
if __name__ == '__main__':
    unittest.main()