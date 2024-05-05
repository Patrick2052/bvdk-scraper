from core.config import settings
from core.db import DatabaseSession
from core.logger import main_logger
import models as mo
import schemas
from datetime import datetime
from scraping.bvdk_page_utils import get_bl_select, get_throbber, get_year_select
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import List
from scraping.exceptions import PageHasNoTableException


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
        main_logger.warn(f"Headers do not fit: given: {
                         headers} || expected: ['Wettkampfdatum', 'Wettkampf', 'Ort', 'Ergebnisse']")

    print(headers)

    trows = tbody.find_elements(By.CSS_SELECTOR, 'tr')

    comps: List[schemas.CompetiotionFromHtmlTable] = []

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

        links = [schemas.LinkInfo(
            text=link.text,
            url=link.get_attribute('href')
        ) for link in links]

        url_to_page = name_row.find_element(
            By.CSS_SELECTOR, 'a').get_property('href')

        comp = schemas.CompetiotionFromHtmlTable(
            date_string=date_row.text,
            name=name_row.text,
            location_string=location_row.text,
            url_to_page=url_to_page,
            links=links
        )

        comps.append(comp)

    return comps


def scrape_bvdk_bundesländer_comps():

    db = DatabaseSession()

    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    driver.get("https://bvdk.de/wettkampfkalenderlv")

    new_scrape = mo.BvdkPageScrape(
        start_time=datetime.now()
    )
    db.add(new_scrape)
    db.commit()
    db.refresh(new_scrape)

    current_year = datetime.now().year

    bl = get_bl_select(driver)

    bundesländer = [bl.text for bl in bl.options]
    years_to_scrape = range(current_year - 3, current_year + 2)

    for year in years_to_scrape:
        print(f"Start {year}")

        # TODO what if no year selet on page
        year_select = get_year_select(driver)
        year_select.select_by_value(str(year))
        time.sleep(1)
        # try:
        #     throbber = get_throbber(driver)
        # except NoSuchElementException as e:
        #     print("No throbber")
        #     raise
        print("wait...")
        WebDriverWait(driver, 10, poll_frequency=0.2).until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, '.ajax-progress-throbber')))
        print("continue...")
        time.sleep(1)

        #! iterate over bls
        for bundesland in bundesländer:
            print(f"Scraping {bundesland} - {year}")
            bl_select = get_bl_select(driver)
            bl_select.deselect_all()
            bl_select.select_by_value(bundesland)
            time.sleep(1)
            print("wait for throbber...")
            WebDriverWait(driver, 10, poll_frequency=0.2).until(EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, '.ajax-progress-throbber')))
            print("continue...")
            time.sleep(1)

            try:
                comps = scrape_comps_table(driver)
                print("table done")
            except PageHasNoTableException:
                main_logger.warn(f"No table on page {bundesland} - {year}")
                continue

            for comp in comps:
                new_comp = mo.ScrapedCompetitionInfo(
                    name=comp.name,
                    date_string=comp.date_string,
                    url_to_page=str(comp.url_to_page),
                    location_string=comp.location_string,
                    competition_year=year,
                    is_bundesland_comp=True,
                    bundesland_string=bundesland,
                    is_national_comp=False,
                    page_scrape_id=new_scrape.id
                )
                db.add(new_comp)
                db.commit()
                db.refresh(new_comp)

                for link in comp.links:
                    new_link = mo.ScrapedLink(
                        url=str(link.url),
                        scraped_competition_id=new_comp.id,
                        text=link.text
                    )
                    db.add(new_link)
                db.commit()

            print(f"{bundesland} done")

    driver.close()
