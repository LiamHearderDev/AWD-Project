import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.system.test_S_base import BaseSeleniumTests
import json, time
from app.models import User
from app.extensions import db
import sqlalchemy as sa
from selenium.common.exceptions import TimeoutException



class TestUserOperations(BaseSeleniumTests):
    
    def click_and_assert(self, link_id, expected_path, expected_id):
        # clicks link and searches for expected element on link page
        self.driver.find_element(By.ID, link_id).click()
        self.wait.until(lambda d: expected_path in d.current_url, message=f"URL {self.driver.current_url} did not contain {expected_path}")
        self.wait.until(EC.presence_of_element_located((By.ID, expected_id)), message=f"Element {expected_id} not found")
    
    def attempt_register(self, username, email, password): # go to register page and register
        self.driver.get(f'{self.base_url}/register')
        self.wait.until(EC.presence_of_element_located((By.ID, 'Register_ID')))
        self.driver.find_element(By.ID, 'register_username').send_keys(username)
        self.driver.find_element(By.ID, 'register_email').send_keys(email)
        self.driver.find_element(By.ID, 'register_password').send_keys(password)
        self.driver.find_element(By.ID, 'register_password2').send_keys(password)
        self.driver.find_element(By.ID, 'register_submit').click()
        time.sleep(1) # allow database time to update
    
    def attempt_login(self, username, password): # login, assuming already on login page
        self.driver.get(f'{self.base_url}/login')
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))
        self.driver.find_element(By.ID, 'login_input_username').send_keys(username)
        self.driver.find_element(By.ID, 'login_input_password').send_keys(password)
        self.driver.find_element(By.ID, 'login_input_submit').click()
    
    def check_logged_in(self): # check if can access profile and logout
        self.wait.until(EC.presence_of_element_located((By.ID, 'Base_Profile')))
        self.wait.until(EC.presence_of_element_located((By.ID, 'Base_Logout')))
    
    def check_logged_out(self): # check if can access login
        self.wait.until(
            EC.presence_of_element_located((By.ID, 'Base_Login')),
            message="Logout did not redirect to login"
        )
    
    def print_all_users(self, tag):
        # Query and print every row in the User table
        time.sleep(0.5)
        with self.app.app_context():
            stmt = sa.select(User)
            users = db.session.execute(stmt).scalars().all()
            print(f"\n--- DB dump ({tag}) ---")
            if not users:
                print("  <no users>")
            for u in users:
                print(f"  id={u.user_id} username={u.username!r} email={u.email!r}")
            print("-----------------------")
    
    def who_am_i(self):
        # issue a GET to /get_current_user and parse the JSON response
        self.driver.get(f"{self.base_url}/get_current_user")
        body = self.driver.find_element(By.TAG_NAME, "body").text
        return json.loads(body)

    def logout_wait(self):
        self.check_logged_in()
        self.driver.find_element(By.ID, "Base_Logout").click()
        time.sleep(0.5)
    
    def test_successful_login(self):
        self.attempt_register('selenium_user', 'sel@gmail.com', 'Password123') # register
        self.attempt_login('selenium_user', 'Password123') # login
        self.check_logged_in()
        self.logout_wait() # logout
        self.check_logged_out() # check if logged out

    def test_register_duplicate_username(self):
        # first registration
        self.attempt_register('dupuser', 'dup@example.com', 'Dup12345')
        self.wait.until(EC.url_contains('/login'))

        # second registration with same username
        self.attempt_register('dupuser', 'newemail@example.com', 'Dup12345')
        self.wait.until(EC.url_contains('/register'))

    def test_register_duplicate_email(self):
        self.attempt_register('uniqueuser', 'same@example.com', 'Uniq12345')
        self.wait.until(EC.url_contains('/login'))

        # second registration with same email
        self.attempt_register('anotheruser', 'same@example.com', 'Other12345')
        self.wait.until(EC.url_contains('/register'))

    def test_login_invalid_credentials(self):
        # register
        self.attempt_register('loginuser', 'login@example.com', 'RightPass1')
        self.wait.until(EC.url_contains('/login'))

        # attempt login with wrong password
        self.attempt_login('loginuser', 'WrongPass')
        self.wait.until(EC.url_contains('/login'))

    def test_login_nonexistent_user(self):
        # login without registering
        self.driver.get(f'{self.base_url}/login')
        self.attempt_login('noone', 'doesntmatter')
        self.wait.until(EC.url_contains('/login'))
    
    def test_friendship(self):
        # register account 1
        self.attempt_register('selenium_user_1', 'sel1@gmail.com', 'Password1234') # register 1
        # register account 2
        self.attempt_register('selenium_user_2', 'sel2@gmail.com', 'Password1235') # register 2
        self.attempt_login('selenium_user_2', 'Password1235') # login to account 2
        self.check_logged_in()
        self.driver.get(f'{self.base_url}/friends') # go to friends
        # send request to account 1
        self.wait.until(EC.presence_of_element_located((By.ID, 'friend_type')))
        self.driver.find_element(By.ID, "friend_type").send_keys('selenium_user_1') 
        self.driver.find_element(By.ID, "friend_submit").click()

        self.logout_wait() # logout
        self.attempt_login('selenium_user_1', 'Password1234') # login to account 1
        self.check_logged_in()
        self.driver.get(f'{self.base_url}/friends') # go to friends
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.accept-btn")))
        self.driver.find_element(By.CSS_SELECTOR, "button.accept-btn").click()
        self.driver.find_element(By.LINK_TEXT, "View Stats").click() # go to friends stats 
        self.wait.until(EC.presence_of_element_located((By.ID, "Stats_ID"))) # on a stats page
        user = self.driver.find_element(By.ID, "user_ID").text
        self.assertEqual(user, 'User: selenium_user_2') # on other user's stats page


if __name__ == '__main__':
    unittest.main()
