from pydantic import BaseModel
from typing import List, Union, Dict

from business.db.insights_service import InsightEngineValues
from project_shkedia_models.collection import CollectionBasic
from project_shkedia_models.media import MediaMetadata
from business.gallery.service import CollectionPreview

class PageMetadata(BaseModel):
    current_page: int  | None
    number_of_pages: int = 1

    @property
    def pages_list(self):
        return (list)(range(1,self.number_of_pages+1))

class BaseCanvas(BaseModel):
    view_type: str
    nav_list: Union[List[MediaMetadata],List[CollectionPreview]]

class BaseContext(BaseModel):
    navigator: Dict[str,List[str]] | None = None
    canvas: BaseCanvas | None = None
    page: PageMetadata | None = None
    upload_url: str = ""
    search_needed: bool = True
    content: dict = {}
