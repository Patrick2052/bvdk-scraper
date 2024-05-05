from core.db import Base

from sqlalchemy import DateTime, Column, String, Integer, ForeignKey, Boolean
import uuid


class BvdkPageScrape(Base):
    __tablename__ = "bvdk_page_scrapes"

    id = Column(String(), primary_key=True, default=(str(uuid.uuid4())))

    start_time = Column(DateTime())
    end_time = Column(DateTime())
    is_finished = Column(Boolean(), default=False)
    # information about the scrape


class ScrapedCompetitionInfo(Base):
    __tablename__ = "scraped_competitions_info"

    id = Column(Integer(), autoincrement=True, primary_key=True)

    name = Column(String())
    date_string = Column(String())
    url_to_page = Column(String())
    location_string = Column(String())
    links = Column(Integer(), ForeignKey("scraped_links.id"))
    competition_year = Column(Integer(), nullable=True)
    is_bundesland_comp = Column(Boolean())
    bundesland_string = Column(String())
    is_national_comp = Column(Boolean())
    start_date = Column(DateTime(), nullable=True)
    end_date = Column(DateTime(), nullable=True)

    page_scrape_id = Column(String(), ForeignKey("bvdk_page_scrapes.id"))


class ScrapedLink(Base):
    __tablename__ = "scraped_links"

    id = Column(Integer(), autoincrement=True, primary_key=True)

    scraped_competition_id = Column(ForeignKey('scraped_competitions_info.id'))
    text = Column(String())
    url = Column(String())
