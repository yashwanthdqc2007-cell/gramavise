from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.config import settings


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Protects endpoints against oversized request bodies.
    
    Rejects requests exceeding MAX_REQUEST_SIZE_BYTES with HTTP 413 Payload Too Large.
    Safely inspects streamed body chunks if Content-Length header is omitted,
    ensuring legitimate small requests without Content-Length are never rejected.
    """

    def __init__(self, app, max_size_bytes: int = settings.MAX_REQUEST_SIZE_BYTES):
        super().__init__(app)
        self.max_size_bytes = max_size_bytes

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Non-mutating methods without body require no inspection
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)

        # 1. Quick validation on Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_size_bytes:
                    req_id = getattr(request.state, "request_id", None)
                    headers = {"X-Request-ID": req_id} if req_id else {}
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"Payload Too Large. Request body size ({length} bytes) exceeds maximum limit of {self.max_size_bytes} bytes."
                        },
                        headers=headers
                    )
            except ValueError:
                pass

        # 2. For requests with missing Content-Length, read and cache body safely
        if not content_length:
            body = await request.body()
            if len(body) > self.max_size_bytes:
                req_id = getattr(request.state, "request_id", None)
                headers = {"X-Request-ID": req_id} if req_id else {}
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Payload Too Large. Request body size ({len(body)} bytes) exceeds maximum limit of {self.max_size_bytes} bytes."
                    },
                    headers=headers
                )

        return await call_next(request)
