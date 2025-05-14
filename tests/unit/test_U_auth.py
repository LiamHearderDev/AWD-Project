import unittest
from app import create_app, db
from app.config import TestingConfig
from app.models import User
from datetime import datetime
from app.forms import LoginForm, RegistrationForm

class AuthBlueprintTestCase(unittest.TestCase):
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
    


    ##### HELPER FUNCTIONS #####

    def attempt_login(self, username: any, password: any, remember_me: any = True):
        """Helper function to attempt login with given username and password."""
        return self.client.post('/login', data={
            'username': username,
            'password': password,
            'remember_me': remember_me
        })

    def attempt_registration(self, username: any, email: any, password: any, password2: any):
        """Helper function to attempt registration with given username, email, password, and password confirmation."""
        return self.client.post('/register', data={
            'username': username,
            'email': email,
            'password': password,
            'password2': password2
        })


    ##### LOGIN PAGE TESTS #####

    def test_login_route_renders_template(self): 
        """Test the login route to ensure it renders the correct template, and returns a 200 status code."""

        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200, "Login route did not return 200.")
        self.assertIn(b'Login_ID', response.data, "Element with id=Login_ID not found in response data.")


    def test_login_user_success(self): 
        """Test the login route to ensure a user can log in successfully, and is redirected to the intro page."""

        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'
        testRegistrationTime = datetime.now()

        with self.app.app_context():
            user = User(username=testUsername, email=testEmail, registration_time=testRegistrationTime)
            user.set_password(testPassword)
            db.session.add(user)
            db.session.commit()

            # check if the user was actually added to the database
            user = User.query.filter_by(username=testUsername).first()
            self.assertIsNotNone(user, "User was not found in the database.")
            self.assertTrue(user.check_password(testPassword), "Password check failed for the registered user.")

        
        # Attempt to log in with valid credentials
        # response = self.attempt_login(testUsername, testPassword, True)
        response = self.client.post('/login', data={
            'username': testUsername,
            'password': testPassword,
            'remember_me': True
        })

        # Check if the response is a successful redirect
        self.assertEqual(response.status_code, 302, "Login route did not return 302, with valid credentials.")
        self.assertEqual(response.location, '/intro', "Post-login redirect location is not correct.")

        # Check if the user is actually logged in
        response = self.client.get('/get_current_user')
        self.assertEqual(response.status_code, 200, "Get current user route did not return 200.")
        self.assertIsNotNone(response, "Get current user route did not return a response.")
        self.assertNotIn(b'User is not logged in.', response.data, "User is not logged in error message not found in response data.")


    def test_login_user_invalid(self):
        """Test the login route to ensure a user cannot log in with invalid credentials.
        This test is designed to provide login details that will pass form validation, but test the login functionality itself."""

        # Create some test data
        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'
        testRegistrationTime = datetime.now()

        # Create a test user
        with self.app.app_context():
            user = User(username=testUsername, email=testEmail, registration_time=testRegistrationTime)
            user.set_password(testPassword)
            db.session.add(user)
            db.session.commit()
        
        # Attempt to log in with invalid password
        response = self.attempt_login(testUsername, 'wrongpassword', True)
        self.assertNotEqual(response.status_code, 302, "Login route returned 302 with an invalid password.") # If we receive a 302, it means the login was successful, which is not what we want.
        self.assertIn(b'Invalid username or password.', response.data, "Invalid login error message not found in response data, for invalid password.")

        # Attempt to log in with invalid username
        response = self.attempt_login('wrongusername', testPassword, True)
        self.assertNotEqual(response.status_code, 302, "Login route returned 302 with an invalid username.") # If we receive a 302, it means the login was successful, which is not what we want.
        self.assertIn(b'Invalid username or password.', response.data, "Invalid login error message not found in response data, for invalid username.")


    def test_logout_user(self):
        """Test the logout route to ensure a user can log out successfully, and is redirected to the intro page."""

        # Create some test data
        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'
        testRegistrationTime = datetime.now()

        # Create a test user
        with self.app.app_context():
            user = User(username=testUsername, email=testEmail, registration_time=testRegistrationTime)
            user.set_password(testPassword)
            db.session.add(user)
            db.session.commit()

        # Log in the user first
        self.attempt_login(testUsername, testPassword, True)

        # Now log out the user
        response = self.client.get('/logout')
        
        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302, "Logout route did not return 302.")
        self.assertEqual(response.location, '/intro', f"Post-logout redirect location is not correct. Should be /intro, but got {response.location}.")

        # Check if the user is logged out
        response = self.client.get('/get_current_user') # Need to get the current user.
        self.assertEqual(response.status_code, 200, "Get current user route did not return 200.")
        self.assertIsNotNone(response, "Get current user route did not return a response.")
        self.assertIn(b'User is not logged in.', response.data, "User is still logged in after logout.")


    def test_login_form_validation(self):
        """Test the login form validation to ensure it works correctly.
        This test is for the form validation logic, not the actual login functionality, by providing a variety of invalid data types."""

        # Create some test data
        testUsername = "testuser"
        testPassword = "testpassword"

        with self.app.app_context():

            ### Invalid data tests ###

            invalidDataTypes = {
                'empty': '',
                'None': None,
                'number': 150,
                'list': [],
                'dict': {}
            }

            # Test invalid data types on username and password
            for key, value in invalidDataTypes.items():
                # Test Usernames
                response = self.attempt_login(value, testPassword, True)
                self.assertNotEqual(response.status_code, 302, f"Login route validated with username: {key}.")

                # Test Passwords
                response = self.attempt_login(testUsername, value, True)
                self.assertNotEqual(response.status_code, 302, f"Login route validated with password: {key}.")

            # Test missing username
            response = self.client.post('/login', 
                data={ 'password': testPassword, 'remember_me': True
            })
            self.assertNotEqual(response.status_code, 302, "Login route validated with missing remember_me.")

            # Test missing password
            response = self.client.post('/login', 
                data={ 'username': testUsername, 'remember_me': True
            })
            self.assertNotEqual(response.status_code, 302, "Login route validated with missing password.")

            # Test missing remember_me
            response = self.client.post('/login',
                data={ 'username': testUsername, 'password': testPassword
            })
            self.assertNotEqual(response.status_code, 302, "Login route validated with missing remember_me.")



    ##### REGISTRATION PAGE TESTS #####

    def test_register_route_renders_template(self): 
        """Test the register route to ensure it renders the correct template, and returns a 200 status code."""

        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200, "Register route did not return 200.")
        self.assertIn(b'Register_ID', response.data, "Element with id=Register_ID not found in response data.")


    def test_register_user_success(self): 
        """Test the registration route to ensure a user can register successfully, and is redirected to the login page."""

        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'
        testRegistrationTime = datetime.now()

        with self.app.app_context():
            user = User(username=testUsername, email=testEmail, registration_time=testRegistrationTime)
            user.set_password(testPassword)

        with self.client:
            # Attempt to register with valid credentials
            response = self.attempt_registration(testUsername, testEmail, testPassword, testPassword)

            # Check if the response is a redirect
            self.assertEqual(response.status_code, 302, f"Register route did not return 302. Got {response.status_code}.")
            self.assertEqual(response.location, '/login', f"Post-registry redirect location is not '/login'. Got {response.location}.")

        # Check if the user was actually added to the database
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user, "User was not found in the database.")
            self.assertTrue(user.check_password('testpassword'), "Password check failed for the registered user.")
    

    def test_register_user_duplicate(self): 
        """Test the registration route to ensure a user cannot register with a duplicate username."""

        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'
        testRegistrationTime = datetime.now()

        with self.app.app_context():
            user = User(username=testUsername, email=testEmail, registration_time=testRegistrationTime)
            user.set_password(testPassword)
            db.session.add(user)
            db.session.commit()
        with self.client:
            # Attempt to register with the same username as someone else
            response = self.attempt_registration(testUsername, "newEmail@example.com", testPassword, testPassword)
            self.assertEqual(response.status_code, 200, "When registering with an already-taken username, the register route did not return 200.")
            self.assertIn(b'This username has been taken.', response.data, "Duplicate username error message not found in response data.")

            # Attempt to register with the same email as someone else
            response = self.attempt_registration('not_taken_yet', testEmail, testPassword, testPassword)
            self.assertEqual(response.status_code, 200, "When registering with an already-taken email, the register route did not return 200.")
            self.assertIn(b'An account is already registered to this email.', response.data, "Duplicate email error message not found in response data.")


    def test_registration_form_validation(self):
        """Test the registration form validation to ensure it works correctly."""

        # Create some test data
        testUsername = 'testuser'
        testPassword = 'testpassword' 
        testEmail = 'testuser@example.com'

        with self.app.app_context():

            # A dictionary of invalid data types
            invalid_data_types = {
                'empty': '',
                'None': None,
                'list': [],
                'dict': {}
            }

            # Loop over the invalid data types and test every field with each type. 
            # If any response is properly validated, the test will fail.
            for key, value in invalid_data_types.items():
                
                # USERNAMES
                response = self.attempt_registration(value, testEmail, testPassword, testPassword)

                self.assertNotEqual(response.status_code, 302, f"Register route validated with username: {key}.")

                # EMAILS
                response = self.attempt_registration(testUsername, value, testPassword, testPassword)
                self.assertNotEqual(response.status_code, 302, f"Register route validated with password: {key}.")

                # PASSWORDS
                response = self.attempt_registration(testUsername, testEmail, value, testPassword)
                self.assertNotEqual(response.status_code, 302, f"Register route validated with password confirm: {key}.")

                # PASSWORD CONFIRMATIONS
                response = self.attempt_registration(testUsername, testEmail, testPassword, value)
                self.assertNotEqual(response.status_code, 302, f"Register route validated with password confirm: {key}.")


            ### Test missing elements ###

            # This is a dictionary of all elements that are required for the registration form.
            # In each row, the key is the element that is missing, and the value is a dictionary of all other elements. (The empty space is where the missing element would be)
            missingElements = {
                'username':     {                          'email': testEmail, 'password': testPassword, 'password2': testPassword  },
                'email':        {'username': testUsername,                     'password': testPassword, 'password2': testPassword  },
                'password':     {'username': testUsername, 'email': testEmail,                           'password2': testPassword  },
                'password2':    {'username': testUsername, 'email': testEmail, 'password': testPassword                             },
            }
            for key, value in missingElements.items():
                response = self.client.post('/register', data=value)
                self.assertNotEqual(response.status_code, 302, f"Register route validated with missing {key}.")


if __name__ == '__main__':
    unittest.main()
    

    

    

