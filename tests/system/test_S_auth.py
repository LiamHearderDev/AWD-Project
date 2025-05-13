import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.system.test_S_base import BaseSeleniumTests

class NavigationTestsLogin(BaseSeleniumTests):
    
    def click_and_assert(self, link_id, expected_path, expected_id):
        # same helper here too
        self.driver.find_element(By.ID, link_id).click()
        self.wait.until(lambda d: expected_path in d.current_url, message=f"URL {self.driver.current_url} did not contain {expected_path}")
        self.wait.until(EC.presence_of_element_located((By.ID, expected_id)), message=f"Element {expected_id} not found")

    def test_navigation_sequence(self):
        # register
        self.driver.get(f'{self.base_url}/register')
        self.wait.until(EC.presence_of_element_located((By.ID, 'Register_ID')))
        self.driver.find_element(By.ID, 'register_username').send_keys('selenium_user')
        self.driver.find_element(By.ID, 'register_email').send_keys('sel@gmail.com')
        self.driver.find_element(By.ID, 'register_password').send_keys('Password123')
        self.driver.find_element(By.ID, 'register_password2').send_keys('Password123')
        self.driver.find_element(By.ID, 'register_submit').click()

        # login
        self.wait.until(EC.presence_of_element_located((By.ID, 'Login_ID')))
        self.driver.find_element(By.ID, 'login_input_username').send_keys('selenium_user')
        self.driver.find_element(By.ID, 'login_input_password').send_keys('Password123')
        self.driver.find_element(By.ID, 'login_input_submit').click()

        # ensure we're logged in
        self.wait.until(EC.presence_of_element_located((By.ID, 'Base_Profile')))
        self.wait.until(EC.presence_of_element_located((By.ID, 'Base_Logout')))

        # check all navigation links work

        # Home
        self.click_and_assert('Base_Home', '/intro', 'Home_ID')
        # Game
        self.click_and_assert('Base_Game', '/game', 'Game_ID')
        # Leaderboard
        self.click_and_assert('Base_Leaderboard', '/leaderboard', 'Leaderboard_ID')
        # Stats
        self.click_and_assert('Base_Stats', '/stats', 'Stats_ID')
        # Profile
        self.click_and_assert('Base_Profile', '/profile', 'Profile_ID')
        # Friends
        self.click_and_assert('Base_Friends', '/friends', 'Friends_ID')
        
        # finally logout
        self.driver.find_element(By.ID, 'Base_Logout').click()
        self.wait.until(
            EC.presence_of_element_located((By.ID, 'Base_Login')),
            message="Logout did not redirect to login"
        )




if __name__ == '__main__':
    unittest.main()
