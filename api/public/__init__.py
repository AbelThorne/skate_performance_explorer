from fastapi import APIRouter, Depends

from api.auth import authent

from api.public import health as health
from api.public import skater as skaters
from api.public import competition as competitions

# from api.public import inscription as inscriptions
from api.public import category as categories
from api.public import performance as performances
from api.public import club as clubs

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
    competitions.router,
    prefix="/competitions",
    tags=["Competitions"],
    dependencies=[Depends(authent)],
)
# api.include_router(
#     inscriptions.router,
#     prefix="/inscriptions",
#     tags=["Inscriptions"],
#     dependencies=[Depends(authent)],
# )
api.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(authent)],
)
api.include_router(
    clubs.router,
    prefix="/clubs",
    tags=["Clubs"],
    dependencies=[Depends(authent)],
)
api.include_router(
    performances.router,
    prefix="/performances",
    tags=["Performances"],
    dependencies=[Depends(authent)],
)
