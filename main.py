from queue import Queue
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from core.logger import main_logger

import subprocess
import time

from scraping.competitions_main import scrape_main_comps, scrape_bundesländer

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

# scrape_main_comps(driver)
scrape_bundesländer(driver)