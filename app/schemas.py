from pydantic import BaseModel

class URLCreateRequest(BaseModel):
    long_url: str

class URLCreateResponse(BaseModel):
    short_code: str
    long_url: str

class StatsResponse(BaseModel):
    short_code: str
    long_url: str
    total_clicks: int