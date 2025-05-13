import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.system.test_S_base import BaseSeleniumTests

class NavigationTestsNoLogin(BaseSeleniumTests):

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

    def test_login(self):
        self.click_and_assert(link_id='Base_Login', expected_path='/login', expected_id='Login_ID')

    def test_stats(self): # check if attempt to access stats redirects to login
        nav_link = self.driver.find_element(By.ID, 'Base_Stats')
        nav_link.click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))

if __name__ == '__main__':
    unittest.main()
