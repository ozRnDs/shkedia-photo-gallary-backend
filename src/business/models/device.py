from pydantic import BaseModel, Field
from typing import Union
from uuid import uuid4
from datetime import datetime

class DeviceRequest(BaseModel):
    device_name: str
    owner_name: str

class Device(BaseModel):
    device_id: str = Field(default_factory=lambda:str(uuid4()))
    device_name: str
    owner_id: str
    created_on: datetime = Field(default_factory=lambda:datetime.now().isoformat())
    status: str = "ACTIVE"

    @staticmethod
    def __sql_create_table__(environment: str):
        sql_template = """CREATE TABLE IF NOT EXISTS devices_"""+environment+""" (
            device_id VARCHAR ( 50 ) PRIMARY KEY,
            device_name VARCHAR ( 50 ) UNIQUE NOT NULL,
            owner_id VARCHAR ( 50 ) NOT NULL REFERENCES users_"""+environment+"""(user_id),
            created_on TIMESTAMP NOT NULL,
            device_status VARCHAR ( 50 )
        )"""
        return sql_template
    
    def __sql_insert__(self, environment: str):
        sql_template = """INSERT INTO devices_"""+environment+""" (
            device_id, device_name, owner_id, created_on, device_status
        ) VALUES (%s, %s, %s, %s, %s)"""
        values = (self.device_id, self.device_name, self.owner_id, self.created_on, self.status)
        return sql_template, values

    @staticmethod
    def __sql_select_item__(field_names, field_values, environment: str):
        sql_template = f"SELECT * FROM devices_{environment} WHERE"
        search_string = []
        sql_values=[]
        for field_index, field_name in enumerate(field_names):
            field_search = f"{field_name} IN (" + ",".join(["%s"]*len(field_values[field_index])) + ")"
            search_string.append(field_search)
            sql_values+=field_values[field_index]
        sql_template += " "+" AND ".join(search_string)
        return sql_template, (tuple)(sql_values)

