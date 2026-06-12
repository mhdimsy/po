from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.modules.dashboard.router import router as dashboard_router
from app.health import router as health_router
from app.modules.events.router import router as events_router
from app.modules.import_factory.router import router as import_router
from app.modules.master_data.router import router as master_data_router
from app.modules.materials.router import router as materials_router
from app.modules.optimizer.router import router as optimizer_router
from app.modules.qc_ncr.router import router as qc_ncr_router
from app.modules.resources.router import router as resources_router
from app.modules.risk.router import router as risk_router
from app.modules.scenarios.router import router as scenarios_router
from app.modules.simulation.router import router as simulation_router


def create_app() -> FastAPI:
    app = FastAPI(title="Digital Twin Prototype API")
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(master_data_router, prefix="/master-data")
    app.include_router(import_router, prefix="/imports")
    app.include_router(resources_router, prefix="/synthetic")
    app.include_router(materials_router, prefix="/synthetic")
    app.include_router(events_router, prefix="/events")
    app.include_router(scenarios_router, prefix="/scenarios")
    app.include_router(simulation_router, prefix="/simulations")
    app.include_router(optimizer_router, prefix="/optimizer")
    app.include_router(qc_ncr_router, prefix="/qc-ncr")
    app.include_router(risk_router, prefix="/risk")
    app.include_router(dashboard_router, prefix="/dashboard")
    return app


app = create_app()
