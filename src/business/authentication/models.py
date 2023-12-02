from django.http import HttpRequest
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    token_header: str | None = None

    def get_token_as_header(self):
        if self.token_header:
            return {"Authorization": self.token_header}
        return {"Authorization": self.token_type + " " + self.access_token}
    
    @staticmethod
    def get_token_from_request(request: HttpRequest):
        if "Authorization" in request.headers:
            return Token(access_token="Unknown", token_type="Unknown", token_header=request.headers["Authorization"])
        raise PermissionError("The request doesn't include token")