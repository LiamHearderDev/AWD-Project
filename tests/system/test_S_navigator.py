import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.system.test_S_base import BaseSeleniumTests

class NavigationTestsNoLogin(BaseSeleniumTests): # test navigation without being logged in

    def setUp(self):
        super().setUp()
        # always start from the home page
        self.driver.get(f'{self.base_url}/')

    def click_and_assert(self, link_id, expected_path, expected_id):
        # click the nav link
        nav_link = self.driver.find_element(By.ID, link_id)
        nav_link.click()

        # wait until URL ends with our expected path
        self.wait.until(lambda d: d.current_url.endswith(expected_path),
                        message=f"URL did not end with {expected_path}"
        )

        # wait until element with expected id appears
        self.wait.until(EC.presence_of_element_located((By.ID, 'expected_id')))


    def test_home(self):
        self.click_and_assert(link_id='Base_Home', expected_path='/intro', expected_id='Home_ID')

    def test_game(self):
        self.click_and_assert(link_id='Base_Game', expected_path='/game', expected_id='Game_ID')

    def test_leaderboard(self):
        self.click_and_assert(link_id='Base_Leaderboard', expected_path='/leaderboard', expected_id='Leaderboard_ID')

    def test_login_register(self): # go to login then register
        self.click_and_assert(link_id='Base_Login', expected_path='/login', expected_id='Login_ID')
        self.click_and_assert(link_id='Login_Register', expected_path='/register', expected_id='Register_ID')

    def test_stats(self): # check if attempt to access stats redirects to login
        nav_link = self.driver.find_element(By.ID, 'Base_Stats')
        nav_link.click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))



class NavigationTestsLogin(BaseSeleniumTests): # test navigation while being logged in

    def click_and_assert(self, link_id, expected_path, expected_id):
        # click the nav link
        nav_link = self.driver.find_element(By.ID, link_id)
        nav_link.click()

        # wait until URL ends with our expected path
        self.wait.until(lambda d: d.current_url.endswith(expected_path),
                        message=f"URL did not end with {expected_path}"
        )

        # wait until element with expected id appears
        self.wait.until(EC.presence_of_element_located((By.ID, 'expected_id')))

    def setUp(self):
        super().setUp()
        # start from home page
        self.driver.get(f'{self.base_url}/') 
        # go to login page
        self.click_and_assert(link_id='Base_Login', expected_path='/login', expected_id='Login_ID')
        # go to registration
        self.click_and_assert(link_id='Login_Register', expected_path='/register', expected_id='Register_ID')
        # register
        self.driver.find_element(By.ID, "register_username").send_keys("selenium_user")
        self.driver.find_element(By.ID, "register_email").send_keys("sel@example.com")
        self.driver.find_element(By.ID, "register_password").send_keys("Password123")
        self.driver.find_element(By.ID, "register_password2").send_keys("Password123")
        self.driver.find_element(By.ID, "register_submit").click()
        # login
        self.wait.until(EC.presence_of_element_located((By.ID, "Login_ID")))
        self.driver.find_element(By.ID, "login_input_username").send_keys("selenium_user")
        self.driver.find_element(By.ID, "login_input_password").send_keys("Password123")
        self.driver.find_element(By.ID, "login_input_submit").click()
        # check if logged in
        self.wait.until(EC.presence_of_element_located((By.ID, "Profile_ID")))
        self.wait.until(EC.presence_of_element_located((By.ID, "Logout_ID")))

    def test_home(self):
        self.click_and_assert(link_id='Base_Home', expected_path='/intro', expected_id='Home_ID')

    def test_game(self):
        self.click_and_assert(link_id='Base_Game', expected_path='/game', expected_id='Game_ID')

    def test_leaderboard(self):
        self.click_and_assert(link_id='Base_Leaderboard', expected_path='/leaderboard', expected_id='Leaderboard_ID')

    def test_stats(self):
        self.click_and_assert(link_id='Base_Stats', expected_path='/stats', expected_id='Stats_ID')


if __name__ == '__main__':
    unittest.main()
