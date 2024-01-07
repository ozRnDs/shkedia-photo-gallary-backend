from cachetools import cached, TTLCache
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List,Dict, Any

from .media_service import MediaDBService
from project_shkedia_models.insights import InsightEngineValues, InsightEngineObjectEnum


class InsightEngineService:
    def __init__(self,
                 db_media_service: MediaDBService) -> None:       
        self.db_media_service = db_media_service        

    @property
    # @cached(cache=TTLCache(maxsize=4, ttl=timedelta(minutes=2), timer=datetime.now))
    def engines(self) -> List[InsightEngineValues]:
        return self.db_media_service.get_all_engines(response_type=InsightEngineObjectEnum.InsightEngineValues)

    def get_engine_name_by_id(self, engine_id):
        for engine in self.engines:
            if engine.id ==engine_id:
                return engine.name
        raise FileNotFoundError(f"Could not find the requested engine: {engine_id}")
