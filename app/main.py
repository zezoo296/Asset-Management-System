from fastapi import FastAPI, Request, Depends
from api.v1.router import router as v1_router
from middleware.rate_limit import RateLimitMiddleware
from core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, ENV, APITALLY_CLIENT_ID
from apitally.fastapi import ApitallyMiddleware

app = FastAPI()

app.add_middleware(
    ApitallyMiddleware,
    client_id=APITALLY_CLIENT_ID,
    env=ENV,

    enable_request_logging=True,

    log_request_headers=ENV == "dev",
    log_request_body= ENV == "dev",    
    log_response_body= ENV == "dev",   

    capture_logs=True,
    capture_traces=True,

    mask_body_fields=[
        r"^password$",
        r"^token$",
        r"^access_token$",
        r"^refresh_token$",
    ],
)


app.include_router(v1_router, prefix="/api/v1")
app.add_middleware(
    RateLimitMiddleware,
    max_requests=RATE_LIMIT_REQUESTS,
    window=RATE_LIMIT_WINDOW
)