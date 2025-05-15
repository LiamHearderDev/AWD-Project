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

    def test_play(self):
        
        text = 'beans on toast'

        self.add_paragraph(body=text, type='normal') # add paragraph to database

        self.driver.get(f'{self.base_url}/') # go to home
        self.click_and_assert('Base_Game', '/game', 'Game_ID') # click to game page
        
        self.driver.find_element(By.ID, 'startButton').click() # start game
        gameText = self.driver.find_element(By.ID, 'gameElement')
        gameText.send_keys(text) # type paragraph

        self.wait.until(EC.presence_of_element_located((By.ID, 'proof_game_finished'))) # check if results displayed




if __name__ == '__main__':
    unittest.main()
