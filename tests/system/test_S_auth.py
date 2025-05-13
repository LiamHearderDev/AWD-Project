import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.system.test_S_base import BaseSeleniumTests

class TestLogin(BaseSeleniumTests):
    
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
    
    def attempt_login(self, username, password): # given on login page, attempt to log in
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
    
    def test_successful_login(self):
        self.attempt_register('selenium_user', 'sel@gmail.com', 'Password123') # register
        self.attempt_login('selenium_user', 'Password123') # login
        self.check_logged_in() # check if logged in
        self.driver.find_element(By.ID, 'Base_Logout').click() # logout
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
        self.attempt_login('noone', 'doesntmatter')
        self.wait.until(EC.url_contains('/login'))


if __name__ == '__main__':
    unittest.main()
