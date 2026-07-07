from fastapi import APIRouter

from src.app.routes.rag.search_routes import router as search_router
from src.app.routes.rag.vector_routes import router as vector_router
from src.app.routes.rag.agentic_routes import router as agentic_router
from src.app.routes.rag.evaluation_routes import router as evaluation_router
from src.app.routes.rag.verification_routes import router as verification_router

router = APIRouter()

router.include_router(search_router)
router.include_router(vector_router)
router.include_router(agentic_router)
router.include_router(evaluation_router)
router.include_router(verification_router)