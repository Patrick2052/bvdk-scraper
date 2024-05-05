from pydantic import (
    BaseModel,
    HttpUrl,
)
from typing import List
from datetime import datetime


class LinkInfo(BaseModel):
    text: str
    url: HttpUrl
    scraped_at: datetime | None = None


class CompetitionInfo(BaseModel):
    name: str
    date_string: str
    url_to_page: HttpUrl | None
    location_string: str
    links: List[LinkInfo] | None = None
    competition_year: int
    is_bundesland_comp: bool | None = None
    is_national_comp: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class CompetiotionFromHtmlTable(BaseModel):
    name: str
    date_string: str
    url_to_page: HttpUrl | None
    location_string: str
    links: List[LinkInfo] | None = None
    scraped_at: datetime