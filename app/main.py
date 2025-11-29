"""Main FastAPI application for Rowboat API SDK Connector."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    OpenWebUIRequest,
    OpenWebUIResponse
)
from app.rowboat_service import RowboatService
from app import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instance
rowboat_service: RowboatService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global rowboat_service
    settings = get_settings()

    # Set debug logging if enabled
    if settings.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    # Initialize Rowboat service
    try:
        rowboat_service = RowboatService(settings)
        logger.info("Rowboat service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Rowboat service: {str(e)}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down application")


app = FastAPI(
    title="Rowboat API SDK Connector",
    description="A headless webservice for Rowboat SDK with OpenWebUI support",
    version=__version__,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_rowboat_service() -> RowboatService:
    """Dependency to get the Rowboat service instance."""
    if rowboat_service is None:
        raise HTTPException(status_code=503, detail="Rowboat service not initialized")
    return rowboat_service


@app.get("/", response_model=HealthResponse)
async def root(service: RowboatService = Depends(get_rowboat_service)):
    """Root endpoint returning service health information."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        rowboat_configured=service.health_check()
    )


@app.get("/health", response_model=HealthResponse)
async def health(service: RowboatService = Depends(get_rowboat_service)):
    """Health check endpoint."""
    is_healthy = service.health_check()
    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        version=__version__,
        rowboat_configured=is_healthy
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: RowboatService = Depends(get_rowboat_service)
):
    """
    Chat endpoint for interacting with Rowboat.

    This endpoint allows you to send messages to Rowboat and receive responses.
    You must provide Rowboat credentials in the request.
    You can optionally provide a conversation_id to continue an existing conversation.
    """
    try:
        logger.info(f"Received chat request with {len(request.messages)} messages")

        result = service.run_turn(
            credentials=request.credentials,
            messages=request.messages,
            conversation_id=request.conversation_id,
            mock_tools=request.mock_tools
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            debug_info=result.get("debug_info")
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/owui", response_model=OpenWebUIResponse)
async def openwebui_function(
    request: OpenWebUIRequest,
    settings: Settings = Depends(get_settings),
    service: RowboatService = Depends(get_rowboat_service)
):
    """
    OpenWebUI compatible endpoint.

    This endpoint is designed to be called from OpenWebUI as a custom function.
    It provides detailed debug information when debug mode is enabled.
    Rowboat credentials must be provided in each request.
    """
    if not settings.enable_owui:
        raise HTTPException(status_code=403, detail="OpenWebUI integration is disabled")

    try:
        # Enable detailed logging if debug is requested
        if request.debug:
            logger.debug("=== OpenWebUI Debug Mode Enabled ===")
            logger.debug(f"Messages: {request.messages}")
            logger.debug(f"Conversation ID: {request.conversation_id}")
            logger.debug(f"Rowboat Host: {request.credentials.host}")
            logger.debug(f"Project ID: {request.credentials.project_id}")

        result = service.run_turn(
            credentials=request.credentials,
            messages=request.messages,
            conversation_id=request.conversation_id
        )

        metadata = {
            "conversation_id": result["conversation_id"],
            "service_version": __version__
        }

        if request.debug or settings.debug:
            metadata["debug"] = {
                "rowboat_host": request.credentials.host,
                "project_id": request.credentials.project_id,
                "messages_count": len(request.messages),
                "debug_info": result.get("debug_info")
            }
            logger.debug(f"Response metadata: {metadata}")

        return OpenWebUIResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            metadata=metadata
        )

    except ValueError as e:
        logger.error(f"Validation error in OWUI: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing OWUI request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    """
    Get current configuration.

    Returns service configuration. Note that Rowboat credentials
    are provided per-request, not configured globally.
    """
    return {
        "mode": "stateless",
        "credentials_required_per_request": True,
        "debug": settings.debug,
        "enable_owui": settings.enable_owui,
        "version": __version__
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
