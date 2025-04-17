import os

import pandas as pd
from sqlalchemy import text
from typing import List, Dict, Literal
from db.utils import get_engine


def with_engine(msg_error: str = "Query error.", echo: bool = False):
    def _with_engine(f):
        def inner(url: str, *args, **kwargs):
            if len(args) > 0:
                raise RuntimeError("You must pass only positional arguments.")

            error = None
            engine = get_engine(url, echo=echo)
            with engine.connect() as conn:
                try:
                    f(conn=conn, **kwargs)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print("TRANSACTION ROLLBACK")
                    print(msg_error)
                    error = e

            engine.dispose()
            if error is not None:
                raise error
        return inner
    return _with_engine


def wrap_insertion(tablename: str, data: Dict | List[Dict], return_values: List[str] = None):
    if isinstance(data, Dict):
        data = [data]

    columns = list(data[0].keys())
    header = f"""INSERT INTO "{tablename}" ("{'","'.join(columns)}") VALUES"""

    body = []
    for d in data:
        values = [str(d[col]) for col in columns]
        body.append(f"({','.join(values)}),")
    body[-1] = body[-1][:-1]
    if return_values:
        body.append(f"""RETURNING ("{'","'.join(return_values)}")""")
    body[-1] = body[-1] + ";"
    return text(f"{header}\n{'\n'.join(body)}")


@with_engine("Table insertions failed.")
def insert_data(conn, data_dir: str, if_exists: Literal["fail", "replace", "append"] = "fail"):
    """function for inserting csv files into tables"""

    table_paths = os.listdir(data_dir)
    table_paths = sorted([path for path in table_paths if path.endswith(".csv")])

    for path in table_paths:
        table_name = os.path.basename(path).split(".")[0].split("-")[1]
        table = pd.read_csv(os.path.join(data_dir, path))
        table.to_sql(name=table_name, con=conn, if_exists=if_exists, index=False)

@with_engine("Views creation failed.")
def manage_views(conn, views: Dict[str, str], if_exists: Literal["fail", "replace"] = "create"):
    """function for controlling views"""

    manage_cmd = "CREATE" if if_exists == "fail" else "CREATE OR REPLACE"
    template = f"""\n{manage_cmd} VIEW"""
    for view_name, view_definition in views.items():
        view_query = f"""{template} {view_name} AS\n{view_definition}"""
        conn.execute(text(view_query))
