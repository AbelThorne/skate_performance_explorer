# from fastapi import APIRouter, Depends, Query
# from sqlmodel import Session

# from commons.schemas import *
# from backend.database import get_session
# from backend.crud.inscription import (
#     create_inscription,
#     read_inscription,
#     read_inscriptions,
#     update_inscription,
#     delete_inscription,
# )


# router = APIRouter()


# @router.post("", response_model=InscriptionRead)
# async def create_an_inscription(
#     inscription: InscriptionCreate, db: Session = Depends(get_session)
# ):
#     return create_inscription(inscription=inscription, db=db)


# @router.get("", response_model=list[InscriptionRead])
# async def get_inscriptions(
#     offset: int = 0,
#     limit: int = Query(default=100, lte=100),
#     db: Session = Depends(get_session),
# ):
#     return read_inscriptions(offset=offset, limit=limit, db=db)


# @router.get("/{inscription_id}", response_model=InscriptionRead)
# async def get_an_inscription(inscription_id: int, db: Session = Depends(get_session)):
#     return read_inscription(inscription_id=inscription_id, db=db)


# @router.patch("/{inscription_id}", response_model=InscriptionRead)
# async def update_an_inscription(
#     inscription_id: int,
#     inscription: InscriptionUpdate,
#     db: Session = Depends(get_session),
# ):
#     return update_inscription(
#         inscription_id=inscription_id, inscription=inscription, db=db
#     )


# @router.delete("/{inscription_id}")
# async def delete_an_inscription(
#     inscription_id: int, db: Session = Depends(get_session)
# ):
#     return delete_inscription(inscription_id=inscription_id, db=db)
