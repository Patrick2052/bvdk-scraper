from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def get_throbber(driver: WebDriver):
    """
    This throbber is shown on the https://bvdk.de/wettkampfkalenderlv
    page when the results are loading   
    """
    throbber = driver.find_element(
        By.CSS_SELECTOR, '.ajax-progress-throbber')
    return throbber


def get_year_select(driver: WebDriver):
    year_selector = driver.find_element(
        By.CSS_SELECTOR, '#edit-field-wettkampfdatum-value-value-year')
    return Select(year_selector)


def get_bl_select(driver: WebDriver):
    """Bundesland select element"""
    s = driver.find_element(
        By.CSS_SELECTOR, '#edit-field-bundeslandverein-value')
    return Select(s)
