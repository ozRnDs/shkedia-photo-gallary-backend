from pydantic import BaseModel, field_validator
from business.db.user_service import UserDBService, User, Device
from business.db.media_service import MediaDBService, MediaDB, SearchResult, MediaObjectEnum, MediaThumbnail, Insight, InsightJob
from typing import List, Any, Dict
from business import utils

class Page(BaseModel):
    page_number: int
    items: Any
    number_of_pages: int

class MediaView(MediaThumbnail):
    thumbnail: str | None = None
    user: User | None = None
    device: Device | None = None
    device_media_uri: str | None = None

    @property
    def canvas_thumbnail(self):
        return self.thumbnail
    
    @property
    def canvas_right_description(self):
        return utils.sizeof_fmt(self.media_size_bytes)
    
    @property
    def canvas_left_description(self):
        return self.created_on.strftime("%d/%m %H:%M")
    
    @property
    def canvas_url_base(self):
        return f"media_view"
    
    @property
    def canvas_url_id(self):
        return self.media_id

class MediaViewInsightCollection(BaseModel):
    insights_list: List[Insight]
    jobs_list: List[InsightJob]

    @property
    def group_insights(self) -> Dict[str,List[Insight]]:
        temp_dict = {}
        for insight in self.insights_list:
            if not insight.name in temp_dict:
                temp_dict[insight.name] = []
            temp_dict[insight.name].append(insight)
        return temp_dict
    


