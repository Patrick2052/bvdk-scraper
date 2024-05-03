from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

from core.logger import main_logger

from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import datetime
import time
from pprint import pprint
import json

class Link(BaseModel):
    text: str
    url: HttpUrl


class CompetitionInfo(BaseModel):
    name: str
    date_string: str
    url_to_page: HttpUrl | None
    location_string: str
    links: List[Link] | None = None


class CompOverall(BaseModel):
    year: str | int
    comps: List[CompetitionInfo]
    bundesland: str | None = None


class MainCompData(BaseModel):
    years: List[CompOverall]

class PageHasNoTableException(Exception):
    pass


def scrape_comps_table(driver: WebDriver):

    tables = driver.find_elements(By.TAG_NAME, 'table')

    if len(tables) > 1:
        main_logger.warning("more than 1 table on page")

    if len(tables) == 0:
        raise PageHasNoTableException()

    table = tables[0]

    tbody = table.find_element(By.TAG_NAME, 'tbody')
    thead = table.find_element(By.TAG_NAME, 'thead')

    headers = [h.text for h in thead.find_elements(By.CSS_SELECTOR, 'tr th')]

    if headers != ['Wettkampfdatum', 'Wettkampf', 'Ort', 'Ergebnisse']:
        main_logger.warn(f"Headers do not fit: given: {headers} || expected: ['Wettkampfdatum', 'Wettkampf', 'Ort', 'Ergebnisse']")

    print(headers)

    trows = tbody.find_elements(By.CSS_SELECTOR, 'tr')

    comps: List[CompetitionInfo] = []

    for row in trows:
        content = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(content) > 4 or len(content) < 4:
            main_logger.warn("to many or to little elements in table row")

        date_row = content[0]
        name_row = content[1]
        location_row = content[2]
        files_row = content[3]

        # extract links
        links = files_row.find_elements(By.CSS_SELECTOR, 'a')

        links = [Link(
            text=link.text,
            url=link.get_attribute('href')
        ) for link in links]

        url_to_page = name_row.find_element(By.CSS_SELECTOR, 'a').get_property('href')

        comp = CompetitionInfo(
            date_string=date_row.text,
            name=name_row.text,
            location_string=location_row.text,
            url_to_page=url_to_page,
            links=links
        )

        comps.append(comp)

    return comps


def scrape_main_comps(driver: WebDriver):
    """
    main function to scrape 

    https://bvdk.de/wettk%C3%A4mpfe
    """

    MAIN_COMPS: List[CompOverall] = list()

    driver.get("https://bvdk.de/wettk%C3%A4mpfe")

    current_year = datetime.now().year

    def get_year_select():
        year_selector = driver.find_element(By.CSS_SELECTOR, '#edit-field-wettkampfdatum-value-value-year')
        return Select(year_selector)

    years = range(current_year - 3, current_year + 2)
    for year in years:
        year_select = get_year_select()
        try:
            year_select.select_by_value(str(year))
            comps = scrape_comps_table(driver)
            MAIN_COMPS.append({
                "year": year,
                "comps": comps
            })
        except NoSuchElementException:
            main_logger.warn("No such element")

    CM = MainCompData(
        years=MAIN_COMPS
    )

    with open("./main_comps.json", "a") as file:
        # file.write(json.dumps(MAIN_COMPS.to, indent=4))
        file.write(CM.model_dump_json(indent=4))
        file.close()

def scrape_bundesländer(driver: WebDriver):
    MAIN_COMPS: List[CompOverall] = list()

    driver.get("https://bvdk.de/wettkampfkalenderlv")

    current_year = datetime.now().year

    def get_year_select():
        year_selector = driver.find_element(By.CSS_SELECTOR, '#edit-field-wettkampfdatum-value-value-year')
        return Select(year_selector)

    def get_bl_select():
        """Bundesland select element"""
        s = driver.find_element(By.CSS_SELECTOR, '#edit-field-bundeslandverein-value')
        return Select(s)

    bl = get_bl_select()
    bl.options

    bundesländer = [bl.text for bl in bl.options]

    years = range(current_year - 3, current_year + 2)
    for year in years:
        print(f"Start {year}")
        year_select = get_year_select()
        try:
            year_select.select_by_value(str(year))
            time.sleep(1)
        except NoSuchElementException:
            main_logger.warn("No such element")
        # for every year go through every bundesland
        for bundesland in bundesländer:
            print(f"Scraping {bundesland} - {year}")
            bl_select = get_bl_select()
            bl_select.select_by_value(bundesland)
            time.sleep(1)

            try:
                comps = scrape_comps_table(driver)
                print("table done")
            except PageHasNoTableException:
                main_logger.warn(f"No table on page {bundesland} - {year}")
                continue
            MAIN_COMPS.append({
                "year": year,
                "comps": comps,
                "bundesland": bundesland
            })
            print(f"{bundesland} done")

    CM = MainCompData(
        years=MAIN_COMPS
    )

    with open("./bl_comps.json", "a") as file:
        # file.write(json.dumps(MAIN_COMPS.to, indent=4))
        file.write(CM.model_dump_json(indent=4))
        file.close()