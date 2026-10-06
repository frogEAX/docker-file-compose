from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import clickhouse_connect
import redis
import os
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

ch = clickhouse_connect.get_client(
    host=CH_HOST, port=CH_PORT,
    username=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
)
r = redis.from_url(REDIS_URL, decode_responses=True)

ch.command("""
    CREATE TABLE IF NOT EXISTS visits (
        path     String,
        ip       String,
        ts       DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY ts
""")


@app.get("/track")
async def track(request: Request):
    path = str(request.query_params.get("path", "/"))
    ip = request.headers.get("x-real-ip") or request.client.host
    ch.insert("visits", [[path, ip, datetime.utcnow()]], column_names=["path", "ip", "ts"])
    r.incr("total_visits")
    return {"ok": True}


@app.get("/stats")
async def stats():
    cached = r.get("stats_cache")
    if cached:
        return json.loads(cached)

    total = int(r.get("total_visits") or 0)

    rows = ch.query("SELECT path, count() as cnt FROM visits GROUP BY path ORDER BY cnt DESC LIMIT 10").result_rows
    top_pages = [{"path": row[0], "count": row[1]} for row in rows]

    rows24 = ch.query("""
        SELECT toHour(ts) as h, count() as cnt
        FROM visits
        WHERE ts >= now() - INTERVAL 24 HOUR
        GROUP BY h ORDER BY h
    """).result_rows
    by_hour = [{"hour": row[0], "count": row[1]} for row in rows24]

    result = {"total": total, "top_pages": top_pages, "by_hour": by_hour}
    r.setex("stats_cache", 10, json.dumps(result))
    return result
