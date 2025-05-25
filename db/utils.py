import os

import sqlalchemy
import inspect
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database, drop_database
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv()


def get_url():
    username = os.getenv("DB_USERNAME")
    host     = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    # port     = os.getenv("DB_PORT")
    driver   = os.getenv("DB_DRIVER")
    name     = os.getenv("DB_NAME")

    url = f"{driver}://{username}:{password}@{host}/{name}"

    if "None" in url:
        raise ValueError("Some environment variable is probably unset.")

    return url


def get_engine(url: str, echo: bool = False) -> sqlalchemy.Engine:
    engine = create_engine(url, echo=echo)
    return engine

def get_session(url: str) -> Session:
    engine = get_engine(url)
    session_pool = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        session = session_pool()
        try:
            yield session
        finally:
            session.close()
    finally:
        session_pool.close_all()
        engine.dispose()


def validate_database(url: str, drop_existing: bool = False) -> bool:
    engine = create_engine(url)
    is_recreated = False
    if not database_exists(engine.url): # Checks for the first time
        create_database(engine.url)     # Create new DB
        print(f"{engine.url}: New Database Created")
        is_recreated = True
    else:
        print(f"{engine.url}: Database Already Exists")
        if drop_existing:
            drop_database(engine.url)
            print(f"{engine.url}: Database Dropped")
            create_database(engine.url)
            print(f"{engine.url}: New Database Created")
            is_recreated = True

    engine.dispose()
    return is_recreated


def get_attributes(
        cls,
        leave_fields: List[str] = None,
        exclude_fields: List[str] = None,
        names_only: bool = True,
        columns: bool = True
) -> List | Dict:

    leave_fields   = [] if leave_fields   is None else leave_fields
    exclude_fields = [] if exclude_fields is None else exclude_fields

    attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
    if columns:
        columns_filter = lambda a: len(a) > 0 and a[0].isupper()
    else:
        columns_filter = lambda _: True
    filter_func = lambda a: not (
            a[0] in exclude_fields or
            (a[0].startswith("__") and a[0].endswith("__")) or
            (a[0].startswith("_") and a[0].endswith("_")) or
            not columns_filter(a[0])
    ) or a[0] in leave_fields
    attributes = dict([attr for attr in attributes if filter_func(attr)])

    if names_only:
        return list(attributes.keys())
    return attributes


def save_db(filename: str):
    username = os.getenv("DB_USERNAME")
    host     = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    port     = os.getenv("DB_PORT")
    # driver   = os.getenv("DB_DRIVER")
    name     = os.getenv("DB_NAME")

    process = subprocess.Popen(
        ['pg_dump',
         '-h', host,
         '-p', str(port),
         '-U', username,
         '-F', 'c',
         '-f', filename,
         name],
        env={'PGPASSWORD': password}
    )
    process.wait()
