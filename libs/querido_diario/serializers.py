from enum import Enum
import abc
from dataclasses import dataclass
from typing import List, Optional
from ..json_serializeble import JSONSerializeble


@dataclass
class Gazette(JSONSerializeble):
    territory_id: str
    date: str
    url: str
    territory_name: str
    state_code: str
    text: str
    theme: str
    subthemes: List[str]
    edition: str
    is_extra_edition: bool
    file_raw_txt: str

    def json(self):
        return {
            "territory_id": self.territory_id,
            "date": self.date,
            "url": self.url,
            "territory_name": self.territory_name,
            "state_code": self.state_code,
            "text": self.text,
            "theme": self.theme,
            "subthemes": self.subthemes,
            "edition": self.edition,
            "is_extra_edition": self.is_extra_edition,
            "file_raw_txt": self.file_raw_txt,
        }


@dataclass
class GazettesResult(JSONSerializeble):
    total_gazettes: int
    gazettes: List[Gazette]

    def json(self):
        return {
            "total_gazettes": self.total_gazettes,
            "gazettes": [gazette.json() for gazette in self.gazettes],
        }

    @classmethod
    def from_json(cls, data: dict):
        return GazettesResult(
            total_gazettes=data['total_gazettes'],
            gazettes=[Gazette(**gazette) for gazette in data['gazettes']],
        )


class SortByEnum(Enum):
    relevance = 'relevance'
    descending_date = 'descending_date'
    ascending_date = 'ascending_date'


@dataclass
class GazetteFilters():
    entities: Optional[List[str]]
    subtheme: Optional[List[str]]
    territory_id: Optional[str]
    since: Optional[str]
    until: Optional[str]
    querystring: Optional[str]
    offset: Optional[int]
    size: Optional[int]
    pre_tags: Optional[str]
    post_tags: Optional[str]
