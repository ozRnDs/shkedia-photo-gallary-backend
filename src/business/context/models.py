from pydantic import BaseModel
from typing import List, Union

from business.db.insights_service import InsightEngineValues
from business.gallery.models import MediaView
from business.gallery.service import CollectionPreview

class PageMetadata(BaseModel):
    current_page: int  | None
    number_of_pages: int = 1

    @property
    def pages_list(self):
        return (list)(range(1,self.number_of_pages+1))

class BaseCanvas(BaseModel):
    view_type: str
    nav_list: Union[List[MediaView],List[CollectionPreview]]

class BaseContext(BaseModel):
    navigator: List[InsightEngineValues] | None = None
    canvas: BaseCanvas | None = None
    page: PageMetadata | None = None
    search_needed: bool = True
    content: dict = {}

