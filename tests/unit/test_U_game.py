import unittest
from app import create_app, db
from app.config import TestingConfig
from app.models import Paragraph
from flask import json

class GameBlueprintTestCase(unittest.TestCase):
    def setUp(self): # setup testing environment
        # create app with test config and context
        self.app = create_app(TestingConfig)
        self.app.config['LOGIN_DISABLED'] = True # make it so that @login_required in routes can accept from anonymous (for testing)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self): # reset testing environment
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

    def test_handle_db_error(self): # checks if error handler for database commit errors is working
        # import the handler directly
        from app.routes.game_routes import handle_db_error
        from sqlalchemy.exc import SQLAlchemyError
        with self.app.app_context():
            rv, status = handle_db_error(SQLAlchemyError('oops')) # manually cause error
        self.assertEqual(status, 500)
        json_data = json.loads(rv.data)
        self.assertEqual(json_data['error'], 'Database error, please try again')

    # NOTE: accepted data to game_routes.py is JSON such that is list with first element being dictionary with all info

    def test_submit_results_non_list(self): # try sending non-JSON data, not list
        response = self.client.post(
            '/submit-instance-statistics',
            json={'not': 'a list'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Expected a JSON array of stats', response.get_json()['error'])

    def test_submit_results_item_not_object(self): # try sending non-JSON data, list but non dictionary element
        response = self.client.post(
            '/submit-instance-statistics',
            json=['string']
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Item 0 must be an object", response.get_json()['error'])

    def test_submit_results_unexpected_description(self): # send data with invalid / unexpected statistic
        payload = [{'description': 'invalid', 'value': 1}]
        response = self.client.post(
            '/submit-instance-statistics', json=payload
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unexpected stat description", response.get_json()['error'])

    def test_submit_results_negative_value(self): # check if any negative numbers
        payload = [{'description': 'total words', 'value': -5}]
        response = self.client.post(
            '/submit-instance-statistics', json=payload
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be non-negative", response.get_json()['error'])
    
if __name__ == '__main__':
    unittest.main()
