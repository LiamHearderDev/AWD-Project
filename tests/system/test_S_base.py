from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import threading, time, unittest
import logging
from werkzeug.serving import make_server


from app import create_app
from app.config import TestingConfig
from app.extensions import db

class BaseSeleniumTests(unittest.TestCase): 

    wait_for_load = False

    # this is how application is setup for all selenium test files
    # all selenium tests should reference BaseSeleniumTests as parent class
    @classmethod
    def setUpClass(cls):
        # don't want to see flask app info for every request
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # start Flask server in background thread
        cls.app = create_app(TestingConfig)
        cls.app.testing = True
    
        cls._srv = make_server('localhost', 5001, cls.app)
        cls.server_thread = threading.Thread(
            target=cls._srv.serve_forever,
            daemon=True
        )
        cls.server_thread.start()

        if cls.wait_for_load: time.sleep(1)  # give server time to start

        # configure headless Chrome properly
        opts = Options()
        opts.add_argument("--headless=new")      

        # additional flags to improve stability in headless mode
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        cls.driver = webdriver.Chrome(options=opts)
        cls.base_url = "http://localhost:5001"

        cls.wait = WebDriverWait(cls.driver, 1)

    @classmethod
    def tearDownClass(cls):
        # quit the Selenium browser
        cls.driver.quit()

        # shut down the Werkzeug server
        cls._srv.shutdown()
        cls.server_thread.join()

        # drop the DB schema and pop the app context
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        # reset DB for each test
        # can override this method in tests, but need to call super().setup() to ensure DB is reset
        with self.app.app_context():
            db.drop_all()
            db.create_all()