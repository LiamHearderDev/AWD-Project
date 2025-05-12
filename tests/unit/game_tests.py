import unittest
from app import create_app, db
from app.config import TestingConfig
from app.models import Paragraph

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

    def test_game_route_renders_template(self): # make sure correct template is successfully sent
        response = self.client.get('/game')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'gameElement', response.data) # check if element with id=gameElement exists, which it should

    def test_random_paragraph_no_content(self): # try get paragraph from empty table
        response = self.client.get('/random-paragraph')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data, {'error': 'no paragraphs available'})

    def test_random_paragraph_success(self): # make sure paragraph is successfully retrieved
        with self.app.app_context(): # add paragraph
            p = Paragraph(body='Test paragraph', type='test')
            db.session.add(p)
            db.session.commit()
            pid = p.paragraph_id
        response = self.client.get('/random-paragraph') # get paragraph
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # still same values
        self.assertEqual(data['paragraph_id'], pid)
        self.assertEqual(data['body'], 'Test paragraph')
        self.assertEqual(data['type'], 'test')

    
if __name__ == '__main__':
    unittest.main()
