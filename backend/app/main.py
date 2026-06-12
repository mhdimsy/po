from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.health import router as health_router
from app.modules.events.router import router as events_router
from app.modules.import_factory.router import router as import_router
from app.modules.master_data.router import router as master_data_router
from app.modules.materials.router import router as materials_router
from app.modules.resources.router import router as resources_router


def create_app() -> FastAPI:
    app = FastAPI(title="Digital Twin Prototype API")
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(master_data_router, prefix="/master-data")
    app.include_router(import_router, prefix="/imports")
    app.include_router(resources_router, prefix="/synthetic")
    app.include_router(materials_router, prefix="/synthetic")
    app.include_router(events_router, prefix="/events")
    return app


app = create_app()
