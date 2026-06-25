from fastapi import FastAPI
from api.v1.router import router as v1_router
from middleware.rate_limit import RateLimitMiddleware
from core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
app = FastAPI()

app.include_router(v1_router, prefix="/api/v1")
app.add_middleware(
    RateLimitMiddleware,
    max_requests=RATE_LIMIT_REQUESTS,
    window=RATE_LIMIT_WINDOW
)