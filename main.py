from queue import Queue
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
import subprocess
import time

options = Options()
driver = webdriver.Firefox(options=options)

driver.get("https://bvdk.de/")

time.sleep(3)

driver.close()

url_queue = Queue()