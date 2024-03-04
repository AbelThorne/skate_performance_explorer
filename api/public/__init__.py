from fastapi import APIRouter, Depends

from api.auth import authent


from api.public.health import views as health
from api.public.skater import views as skaters
from api.public.inscription import views as inscriptions
from api.public.competition import views as competitions
from api.public.performance import views as performances
from api.public.club import views as clubs


api = APIRouter()


api.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
    dependencies=[Depends(authent)],
)
api.include_router(
    skaters.router,
    prefix="/skaters",
    tags=["Skaters"],
    dependencies=[Depends(authent)],
)
api.include_router(
    clubs.router,
    prefix="/clubs",
    tags=["Clubs"],
    dependencies=[Depends(authent)],
)
api.include_router(
    competitions.router,
    prefix="/competitions",
    tags=["Competitions"],
    dependencies=[Depends(authent)],
)
api.include_router(
    inscriptions.router,
    prefix="/inscriptions",
    tags=["Inscriptions"],
    dependencies=[Depends(authent)],
)
api.include_router(
    performances.router,
    prefix="/performances",
    tags=["Performances"],
    dependencies=[Depends(authent)],
)
