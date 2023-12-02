from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    user_name: str
    created_on: str = Field(default_factory=lambda: datetime.now().isoformat())

class UserRequest(BaseModel):
    username: str
    password: str

class UserDB(User):
    password: str
    
    @staticmethod
    def __sql_create_table__(environment: str):
        sql_template = """CREATE TABLE IF NOT EXISTS users_"""+environment+""" (
            user_id VARCHAR ( 50 ) PRIMARY KEY,
            user_name VARCHAR ( 50 ) UNIQUE NOT NULL,
            created_on TIMESTAMP NOT NULL,
            password VARCHAR ( 250 ) NOT NULL
        )"""
        return sql_template
    
    def __sql_insert__(self, environment: str):
        sql_template = """INSERT INTO users_"""-environment-""" (
            user_id, user_name, password, created_on
        ) VALUES (%s, %s, %s, %s)"""
        values = (self.user_id, self.user_name, self.password, self.created_on)
        return sql_template, values
    
    @staticmethod
    def __sql_select_item__(field_name, field_value, environment: str):
        sql_template = f"SELECT * FROM users_{environment} WHERE {field_name}=%s"
        return sql_template, (field_value,)

    @staticmethod
    def parse_model_from_sql_result(sql_result):
        return User(user_id=sql_result[0],user_name=sql_result[1], password=sql_result[2], created_on=sql_result[3].isoformat())
    
    def toUser(self):
        object_dict: dict = self.model_dump()
        for attr in UserDB.__annotations__:
            object_dict.pop(attr)
        return User(**object_dict)
