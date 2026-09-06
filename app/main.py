from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.database import engine, Base, get_db
from app.models import URL, Click
from app.schemas import URLCreateRequest, URLCreateResponse, StatsResponse
from app.core.shortcode import encode
from sqlalchemy.orm import Session

import redis
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()
redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

@app.get("/")
def root():
    return {"message": "URL Shortener API running"}



@app.post("/shorten", response_model=URLCreateResponse)
def shorten_url(request: URLCreateRequest, http_request: Request, db: Session = Depends(get_db)):
    client_ip = http_request.client.host
    key = f"ratelimit:{client_ip}"

    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 60)

    if count > 5:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")

    new_url = URL(long_url=request.long_url, short_code="temp")
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    short_code = encode(new_url.id)
    new_url.short_code = short_code
    db.commit()
    return URLCreateResponse(short_code=short_code, long_url=new_url.long_url)

@app.get("/stats/{code}", response_model=StatsResponse)
def get_stats(code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Short code not found")

    total_clicks = db.query(Click).filter(Click.url_id == url_entry.id).count()

    return StatsResponse(
        short_code=url_entry.short_code,
        long_url=url_entry.long_url,
        total_clicks=total_clicks
    )

@app.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    cached = redis_client.get(code)

    if cached:
        url_id, long_url = cached.split("|", 1)
        new_click = Click(url_id=int(url_id))
        db.add(new_click)
        db.commit()
        return RedirectResponse(url=long_url)

    url_entry = db.query(URL).filter(URL.short_code == code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short code not found")

    redis_client.set(code, f"{url_entry.id}|{url_entry.long_url}")

    new_click = Click(url_id=url_entry.id)
    db.add(new_click)
    db.commit()

    return RedirectResponse(url=url_entry.long_url)