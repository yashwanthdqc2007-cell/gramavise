import uuid
import traceback
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.utils.logging import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Correlation ID middleware for tracking individual requests across the pipeline.
    
    Accepts an existing 'X-Request-ID' header or generates a fresh UUID4.
    Attaches the ID to request.state and guarantees the header is echoed in all responses,
    including caught unhandled server exceptions.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming_id = request.headers.get("X-Request-ID")
        if incoming_id and len(incoming_id) <= 128 and all(c.isalnum() or c in "-_" for c in incoming_id):
            request_id = incoming_id
        else:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            logger.error(f"[RequestID: {request_id}] Unhandled server exception: {exc}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An unexpected server error occurred. Please contact support or try again shortly.",
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )
