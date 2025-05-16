import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.system.test_S_base import BaseSeleniumTests

from app.extensions import db
from app.models import Paragraph

class TestLogin(BaseSeleniumTests):

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

    def add_paragraph(self, body, type='normal'): # add a new paragraph to the database
        with self.app.app_context():
            # check to not add empty paragraph
            if not body or not body.strip():
                raise ValueError("Paragraph body cannot be empty")
            
            # check to see if paragraph has valid / recognisable characters
            allowed_characters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?-'")
            for character in body:
                if character not in allowed_characters:
                    raise ValueError(f"Paragraph contains invalid character {character}")

            new_paragraph = Paragraph(body=body.strip(), type=type)
            db.session.add(new_paragraph)
            db.session.commit()
            return new_paragraph

    def test_play(self): # plays one instance of the game while not logged in
        
        text = 'beans on toast'

        self.add_paragraph(body=text, type='normal') # add paragraph to database

        self.driver.get(f'{self.base_url}/') # go to home
        self.click_and_assert('Base_Game', '/game', 'Game_ID') # click to game page
        self.driver.find_element(By.ID, 'startButton').click() # start game
        gameText = self.driver.find_element(By.ID, 'gameElement')
        gameText.send_keys(text) # type paragraph
        
        # check if game finished
        restart = self.wait.until(EC.visibility_of_element_located((By.ID, "restartButtons")))
        self.assertTrue(restart.is_displayed())

    def test_stats_update(self): # checks if playing the game dynamically changes stats and leaderboard
        
        text = 'beans on toast'
        self.add_paragraph(body=text, type='normal') # add paragraph to database

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

        # check value of total attempts in stats
        self.driver.get(f'{self.base_url}/stats')
        tbody = self.driver.find_element(By.ID, "table_1_body_ID")
        first_row = tbody.find_elements(By.TAG_NAME, "tr")[0] # first row
        cells = first_row.find_elements(By.TAG_NAME, "td") # get all elements of first row
        total_attempts_1 = cells[1].text # get total attempts from all table, 2nd column of first row

        # play the game
        self.driver.get(f'{self.base_url}/') # go to home
        self.click_and_assert('Base_Game', '/game', 'Game_ID') # click to game page
        self.driver.find_element(By.ID, 'startButton').click() # start game
        gameText = self.driver.find_element(By.ID, 'gameElement')
        self.wait.until(EC.element_to_be_clickable((By.ID, 'gameElement')))
        gameText.send_keys(text) # type paragraph
        # check if game finished
        restart = self.wait.until(EC.visibility_of_element_located((By.ID, "restartButtons")))
        self.assertTrue(restart.is_displayed())

        # make sure stats is updated
        self.driver.get(f'{self.base_url}/stats')
        tbody = self.driver.find_element(By.ID, "table_1_body_ID")
        first_row = tbody.find_elements(By.TAG_NAME, "tr")[0] # first row
        cells = first_row.find_elements(By.TAG_NAME, "td") # get all elements of first row
        total_attempts_2 = cells[1].text # get total attempts from all table, 2nd column of first row

        self.assertNotEqual(total_attempts_1, total_attempts_2, f"expected total attempts to change, but both are [{total_attempts_1}]")





if __name__ == '__main__':
    unittest.main()
