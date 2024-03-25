from sqlmodel import Session, SQLModel, create_engine

from config import settings

# connect_args = {"check_same_thread": False}
connect_args = {}
engine = create_engine(settings.DATABASE_URI, echo=True, connect_args=connect_args)


def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    import sqlite3

    conn = sqlite3.connect(settings.DATABASE_URI)
    conn.close()
