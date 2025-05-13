import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.system.test_S_base import BaseSeleniumTests

class NavigationTestsNoLogin(BaseSeleniumTests):
    def setUp(self):
        super().setUp()
        self.driver.get(f'{self.base_url}/')

    def click_and_assert(self, link_id, expected_path, expected_id):
        # Click the nav link
        self.driver.find_element(By.ID, link_id).click()

        # Wait until URL ends with expected_path
        self.wait.until(
            lambda d: d.current_url.endswith(expected_path),
            message=f"URL did not end with {expected_path}"
        )

        # Wait for the unique element on that page
        self.wait.until(
            EC.presence_of_element_located((By.ID, expected_id)),
            message=f"Element {expected_id} not found"
        )

    def test_home(self):
        self.click_and_assert('Base_Home', '/intro', 'Home_ID')

    def test_game(self):
        self.click_and_assert('Base_Game', '/game', 'Game_ID')

    def test_leaderboard(self):
        self.click_and_assert('Base_Leaderboard', '/leaderboard', 'Leaderboard_ID')

    def test_login_and_register(self):
        self.click_and_assert('Base_Login', '/login', 'Login_ID')
        self.click_and_assert('Login_Register', '/register', 'Register_ID')

    def test_stats_redirects_to_login(self):
        # Stats link should bounce you to login
        self.driver.find_element(By.ID, 'Base_Stats').click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')),
                        message="Did not redirect to login on stats link")

class NavigationTestsLogin(BaseSeleniumTests):
    def setUp(self):
        super().setUp()
        self.driver.get(f'{self.base_url}/')
        # Register & log in
        self.driver.find_element(By.ID, 'Base_Login').click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))
        self.driver.find_element(By.ID, 'Login_Register').click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'Register_ID')))
        # Fill in the register form
        self.driver.find_element(By.ID, 'register_username').send_keys('selenium_user')
        self.driver.find_element(By.ID, 'register_email').send_keys('sel@example.com')
        self.driver.find_element(By.ID, 'register_password').send_keys('Password123')
        self.driver.find_element(By.ID, 'register_password2').send_keys('Password123')
        self.driver.find_element(By.ID, 'register_submit').click()
        # Now log in
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))
        self.driver.find_element(By.ID, 'login_input_username').send_keys('selenium_user')
        self.driver.find_element(By.ID, 'login_input_password').send_keys('Password123')
        self.driver.find_element(By.ID, 'login_input_submit').click()
        # Confirm we see profile/logout links
        self.wait.until(EC.presence_of_element_located((By.ID, 'Profile_ID')))
        self.wait.until(EC.presence_of_element_located((By.ID, 'Base_Logout')))

    def click_and_assert(self, link_id, expected_path, expected_id):
        # same helper here too
        self.driver.find_element(By.ID, link_id).click()
        self.wait.until(lambda d: d.current_url.endswith(expected_path))
        self.wait.until(EC.presence_of_element_located((By.ID, expected_id)))

    def test_home(self):
        self.click_and_assert('Base_Home', '/intro', 'Home_ID')

    def test_game(self):
        self.click_and_assert('Base_Game', '/game', 'Game_ID')

    def test_leaderboard(self):
        self.click_and_assert('Base_Leaderboard', '/leaderboard', 'Leaderboard_ID')

    def test_stats(self):
        self.click_and_assert('Base_Stats', '/stats', 'Stats_ID')

if __name__ == '__main__':
    unittest.main()
