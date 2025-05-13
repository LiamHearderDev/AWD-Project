import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.system.test_S_base import BaseSeleniumTests

class NavigationTestsNoLogin(BaseSeleniumTests):

    def setUp(self):
        super().setUp()
        # always start from the home page
        self.driver.get(f'{self.base_url}/')

    def click_and_assert(self, link_id, expected_path):
        # click the nav link
        nav_link = self.driver.find_element(By.ID, link_id)
        nav_link.click()

        # wait until URL ends with our expected path
        self.wait.until(lambda d: d.current_url.endswith(expected_path),
                        message=f"URL did not end with {expected_path}"
        )

    def test_home(self):
        # click to go to home page and wait for URL
        self.click_and_assert(link_id='Base_Home', expected_path='/intro')
        # then wait for the Home page’s unique element to appear
        self.wait.until(EC.presence_of_element_located((By.ID, 'Home_ID')))

    def test_game(self):
        self.click_and_assert(link_id='Base_Game', expected_path='/game')
        self.wait.until(EC.presence_of_element_located((By.ID, 'Game_ID')))

    def test_leaderboard(self):
        self.click_and_assert(link_id='Base_Leaderboard', expected_path='/leaderboard')
        self.wait.until(EC.presence_of_element_located((By.ID, 'Leaderboard_ID')))

    def test_login(self):
        self.click_and_assert(link_id='Base_Login', expected_path='/login')
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))

if __name__ == '__main__':
    unittest.main()
