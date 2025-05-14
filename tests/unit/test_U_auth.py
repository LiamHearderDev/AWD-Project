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
        

    def test_login_route_renders_template(self): 
        """Test the login route to ensure it renders the correct template, and returns a 200 status code."""

        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200, "Login route did not return 200.")
        self.assertIn(b'Login_ID', response.data, "Element with id=Login_ID not found in response data.")



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
            response = self.client.post('/register', data={
                'username': testUsername,
                'email': testEmail,
                'password': testPassword,
                'password2': testPassword
            })

            # Check if the response is a redirect
            self.assertEqual(response.status_code, 302, "Register route did not return 302.")
            self.assertEqual(response.location, '/login', "Post-registry redirect location is not correct.")

        # Check if the user was actually added to the database
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user, "User was not found in the database.")
            self.assertTrue(user.check_password('testpassword'), "Password check failed for the registered user.")
    


    def test_register_user_duplicate_username(self): 
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
            response = self.client.post('/register', data={
                'username': testUsername,
                'password': testPassword,
                'confirm_password': testPassword,
                'email': testEmail,
                'registration_time': testRegistrationTime
            })
            self.assertEqual(response.status_code, 200, "Register route did not return 200.")
            self.assertIn(b'This username has been taken.', response.data, "Duplicate username error message not found in response data.")



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
        
        
        # response = self.client.post('/login', data=form.data, follow_redirects=True)
        response = self.client.post('/login', data={
            'username': testUsername,
            'password': testPassword,
            'remember_me': True
        })

        # Check if the response is a successful redirect
        self.assertEqual(response.status_code, 302, "Login route did not return 302.")
        self.assertEqual(response.location, '/intro', "Post-login redirect location is not correct.")

        # Check if the user is actually logged in
        response = self.client.get('/get_current_user')
        self.assertEqual(response.status_code, 200, "Get current user route did not return 200.")
        self.assertIsNotNone(response, "Get current user route did not return a response.")
        self.assertNotIn(b'User is not logged in.', response.data, "User is not logged in error message not found in response data.")



    def test_login_user_invalid(self):
        """Test the login route to ensure a user cannot log in with invalid credentials."""

        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'
        testRegistrationTime = datetime.now()

        with self.app.app_context():
            user = User(username=testUsername, email=testEmail, registration_time=testRegistrationTime)
            user.set_password(testPassword)
            db.session.add(user)
            db.session.commit()
        
        response = self.client.post('/login', data={
            'username': testUsername,
            'password': 'wrongpassword',
            'remember_me': True
        })
        self.assertEqual(response.status_code, 200, "Login route did not return 200.")
        self.assertIn(b'Invalid username or password.', response.data, "Invalid login error message not found in response data.")



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
        self.client.post('/login', data={
            'username': testUsername,
            'password': testPassword,
            'remember_me': True
        })

        # Now log out the user
        response = self.client.get('/logout')
        
        self.assertEqual(response.status_code, 302, "Logout route did not return 302.")
        self.assertEqual(response.location, '/intro', "Post-logout redirect location is not correct.")
        # Check if the user is logged out
        response = self.client.get('/get_current_user')
        self.assertEqual(response.status_code, 200, "Get current user route did not return 200.")
        self.assertIsNotNone(response, "Get current user route did not return a response.")
        self.assertIn(b'User is not logged in.', response.data, "User is still logged in after logout.")



    def test_login_form_validation(self):
        """Test the login form validation to ensure it works correctly."""

        # Create some test data
        testUsername = 'testuser'
        testPassword = 'testpassword'

        with self.app.app_context():
            
            ### Valid data test ###

            form = LoginForm(username='testuser', password='testpassword', remember_me=True)
            self.assertTrue(form.validate(), "Login form validation failed with valid data.")


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
                form = LoginForm(username=value, password=testPassword, remember_me=True)
                self.assertFalse(form.validate(), f"Login form validation passed with invalid username datatype: {key}.")

                # Test Passwords
                form = LoginForm(username=testUsername, password=value, remember_me=True)
                self.assertFalse(form.validate(), f"Login form validation passed with invalid password datatype: {key}.")

            # Test missing elements
            form = LoginForm(username=testUsername, password=testPassword)
            self.assertFalse(form.validate(), "Login form validation passed with missing remember_me.")
            form = LoginForm(username=testUsername, remember_me=True)
            self.assertFalse(form.validate(), "Login form validation passed with missing password.")
            form = LoginForm(password=testPassword, remember_me=True)
            self.assertFalse(form.validate(), "Login form validation passed with missing username.")
            form = LoginForm(username=testUsername, password=testPassword, remember_me=None)
            self.assertFalse(form.validate(), "Login form validation passed with remember_me as None.")
    

    def test_registration_form_validation(self):
        """Test the registration form validation to ensure it works correctly."""

        # Create some test data
        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = 'testuser@example.com'

        with self.app.app_context():

            ### Valid data ###

            form = RegistrationForm(username=testUsername, email=testEmail, password=testPassword, password2=testPassword)
            self.assertTrue(form.validate(), "Registration form validation failed with valid data.")


            ### Invalid data tests ###

            invalidDataTypes = {
                'empty': '',
                'None': None,
                'number': 150,
                'list': [],
                'dict': {}
            }


            for key, value in invalidDataTypes.items():
                
                # USERNAMES
                response = self.client.post('/register', 
                    data={ 'username': value, 'email': testEmail, 'password': testPassword, 'confirm_password': testPassword
                })
                self.assertNotEqual(response.status_code, 302, f"Register route validated with username: {key}.")

                # EMAILS
                response = self.client.post('/register', 
                    data={ 'username': testUsername, 'email': value, 'password': testPassword, 'confirm_password': testPassword
                })
                self.assertNotEqual(response.status_code, 302, f"Register route validated with password: {key}.")

                # PASSWORDS
                response = self.client.post('/register', 
                    data={ 'username': testUsername, 'email': testEmail, 'password': value, 'confirm_password': testPassword
                })
                self.assertNotEqual(response.status_code, 302, f"Register route validated with password confirm: {key}.")

                # PASSWORD CONFIRMATIONS
                response = self.client.post('/register', 
                    data={ 'username': testUsername, 'email': testEmail, 'password': testPassword, 'confirm_password': value
                })
                self.assertNotEqual(response.status_code, 302, f"Register route validated with password confirm: {key}.")

                # REGISTRATION TIME
                response = self.client.post('/register', 
                    data={ 'username': testUsername, 'email': testEmail, 'password': testPassword, 'confirm_password': testPassword
                })
                self.assertNotEqual(response.status_code, 302, f"Register route validated with registration time: {key}.")

            # Test missing elements
            missingElements = {
                'username':     {                          'email': testEmail, 'password': testPassword, 'password2': testPassword  },
                'email':        {'username': testUsername,                     'password': testPassword, 'password2': testPassword  },
                'password':     {'username': testUsername, 'email': testEmail,                           'password2': testPassword  },
                'password2':    {'username': testUsername, 'email': testEmail, 'password': testPassword                             },
            }
            for key, value in missingElements.items():
                response = self.client.post('/register', data=value)
                self.assertNotEqual(response.status_code, 302, f"Register route validated with missing {key}.")
    

    def test_login_disabled(self):
        """Test the login route to ensure it is disabled when LOGIN_DISABLED is set to True."""

        testUsername = 'testuser'
        testPassword = 'testpassword'
        testEmail = '