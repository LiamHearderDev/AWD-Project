import unittest
from selenium.webdriver.common.by import By
from tests.system.base_test import BaseSeleniumTests

class NavigationTestsNoLogin(BaseSeleniumTests):

    def setUp(self):
        super().setUp()
        # always start from the home page
        self.driver.get(f'{self.base_url}/')
    
    def click_and_assert(self, link_id, expected_path, verify_locator):
        # find the nav link by its id and click it
        nav_link = self.driver.find_element(By.ID, link_id)
        nav_link.click()

        # small wait for the page to load
        self.driver.implicitly_wait(1)

        # make sure URL ended up where we expect
        self.assertTrue(self.driver.current_url.endswith(expected_path), 
                        f"Expected URL to end with {expected_path} but was {self.driver.current_url}")

    def test_home(self):
        self.click_and_assert(link_id='Base_Home', expected_path='/')
        self.driver.find_element(By.ID, 'Home_ID')

if __name__ == '__main__':
    unittest.main()
