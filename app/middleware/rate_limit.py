from collections import defaultdict, deque
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = int(max_requests)
        self.window = int(window)
        self.requests = defaultdict(deque)

    async def dispatch(self, request, call_next):
        ip = request.client.host
        now = time()

        history = self.requests[ip]

        while history and history[0] <= now - self.window:
            history.popleft()

        if len(history) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
            )

        history.append(now)

        return await call_next(request)