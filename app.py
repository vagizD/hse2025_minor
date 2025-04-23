import os
import subprocess

from db.utils import get_url, validate_database, save_db
from db.queries import insert_data, manage_views, save_views
from db.views import VIEWS


DATA_PATH = os.path.join("db", "data")


def main():
    # get db url
    url = get_url()

    # create db if it does not exist
    is_recreated = validate_database(url)

    # create migrations if applicable and run them
    commit_message = "INIT" if is_recreated else "AUTO_GENERATED_COMMIT"
    # subprocess.run(['alembic', 'revision', '--autogenerate', '-m', f'"{commit_message}"'])  # new revision
    subprocess.run(['alembic', 'upgrade', 'head'])                                          # upgrade head

    # insert initial data
    if is_recreated:
        insert_data(url, data_dir=DATA_PATH, if_exists="append")
        manage_views(url, views=VIEWS, if_exists="fail")
    else:
        manage_views(url, views=VIEWS, if_exists="replace")
    save_views(url, path=os.path.join("db", "views"))
    save_db("db.dump")


if __name__ == "__main__":
    main()
