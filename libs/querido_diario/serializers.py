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
    excerpt: str
    subthemes: List[str]
    entities: List[str]
    txt_url: str
    is_extra_edition: Optional[bool] = None
    edition: Optional[str] = None

    def json(self):
        return {
            "territory_id": self.territory_id,
            "date": self.date,
            "url": self.url,
            "territory_name": self.territory_name,
            "state_code": self.state_code,
            "excerpt": self.excerpt,
            "edition": self.edition,
            "subthemes": self.subthemes,
            "entities": self.entities,
            "is_extra_edition": self.is_extra_edition,
            "txt_url": self.txt_url,
        }


@dataclass
class GazettesResult(JSONSerializeble):
    total_gazettes: int
    gazettes: List[Gazette]

    def json(self):
        return {
            "total_excerpts": self.total_gazettes,
            "excerpts": [gazette.json() for gazette in self.gazettes],
        }

    @classmethod
    def from_json(cls, data: dict):
        return GazettesResult(
            total_gazettes=data['total_excerpts'],
            gazettes=[Gazette(**gazette) for gazette in data['excerpts']],
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

    def json(self):
        return {
            "entities": self.entities,
            "subtheme": self.subtheme,
            "territory_id": self.territory_id,
            "since": self.since,
            "until": self.until,
            "querystring": self.querystring,
            "offset": self.offset,
            "size": self.size,
            "pre_tags": self.pre_tags,
            "post_tags": self.post_tags,
        }
