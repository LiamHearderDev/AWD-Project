
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import threading, time, unittest

from app import create_app
from app.config import TestingConfig
from app.extensions import db

class BaseSeleniumTests(unittest.TestCase): 
    # this is how application is setup for all selenium test files
    # all selenium tests should reference BaseSeleniumTests as parent class
    @classmethod
    def setUpClass(cls):
        # Start Flask server in background thread
        cls.app = create_app(TestingConfig)
        cls.app.testing = True
        cls.server_thread = threading.Thread(
            target=cls.app.run,
            kwargs={'port': 5001, 'use_reloader': False}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # give server time to start

        # headless Chrome
        opts = Options()
        opts.headless = True
        cls.driver = webdriver.Chrome(options=opts)
        cls.base_url = 'http://localhost:5001'

    @classmethod
    def tearDownClass(cls):
        # Close browser; server stops when main thread ends
        cls.driver.quit()

    def setUp(self):
        # reset DB for each test
        # can override this method in tests, but need to call super().setup() to ensure DB is reset
        with self.app.app_context():
            db.drop_all()
            db.create_all()

