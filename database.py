import sqlite3 as sqlite
from contextlib import closing

from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_record):
        self.id = user_record.account_id
        self.username = user_record.username
        self.password = user_record.password

class Record:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Record<{', '.join(f'{k}={v}' for k,v in self.__dict__.items())}>"

    def to_user(self) -> User:
        return User(self)


class Database:
    database: sqlite.Connection

    def __init__(self):
        self.connection = sqlite.connect("database/inventory.db", check_same_thread=False)
        self.connection.row_factory = self.__dict_factory

        self.__init_db()

    @staticmethod
    def __dict_factory(cursor: sqlite.Cursor, row) -> dict[str, any]:
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def __init_db(self):
        with open("database/schema.sql") as schema_file:
            schema: str = schema_file.read()

        self.execute(schema)

    def fetch(self, query: str, params: tuple[any] = ()) -> None | list[Record]:
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, params)
            results: list[sqlite.Row] = cursor.fetchall()

        return [Record(item) for item in results]

    def execute(self, query: str, params: tuple[any] = ()) -> None:
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, params)
            self.connection.commit()
