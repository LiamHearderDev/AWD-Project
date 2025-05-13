import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.system.test_S_base import BaseSeleniumTests


class NavigationTestsNoLogin(BaseSeleniumTests):
    def setUp(self): # can access all pages from home
        super().setUp()
        self.driver.get(f'{self.base_url}/')

    def click_and_assert(self, link_id, expected_path, expected_id):
        # click the nav link
        self.driver.find_element(By.ID, link_id).click()

        # wait until URL ends with expected_path
        self.wait.until(
            lambda d: expected_path in d.current_url,
            message=f"URL did not contain {expected_path}"
        )

        # wait for the unique element on that page
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
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')), message="Did not redirect to login on stats link")

if __name__ == '__main__':
    unittest.main()
