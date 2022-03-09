import sys

from PySide2.QtSql import QSqlDatabase, QSqlQuery
from PySide2.QtWidgets import QMessageBox


class ItchificationDB:
    def __init__(self):
        self.dbconn = QSqlDatabase.addDatabase("QSQLITE")
        self.dbconn.setDatabaseName("itchification.sqlite")

        if not self.dbconn.open():
            QMessageBox.critical(
                None,
                "App Name - Error!",
                "Database Error: %s" % self.dbconn.lastError().databaseText(),
            )
            sys.exit(1)

        self.check_table_exists()

    def create_tables(self):
        db = self.dbconn.database()
        create_followed_table = QSqlQuery(db)
        if not create_followed_table.exec_(
            """
            CREATE TABLE IF NOT EXISTS followed (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                userid VARCHAR(60) NOT NULL,
                description TEXT(255) NOT NULL,
                display_name VARCHAR(50) NOT NULL,
                view_count INT NOT NULL,
                UNIQUE(userid)
            );
            """
        ):
            print(self.dbconn.lastError().databaseText())

        create_auth_table = QSqlQuery(db)
        if not create_auth_table.exec_(
            """
                    CREATE TABLE IF NOT EXISTS auth (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                        usertoken VARCHAR(60) NOT NULL,
                        UNIQUE(usertoken)
                    );
                    """
        ):
            print(self.dbconn.lastError().databaseText())

    def check_table_exists(self):
        if "auth" in self.dbconn.tables():
            return
        self.create_tables()

    @staticmethod
    def insert_followed(followed_list):
        insert_query = QSqlQuery()

        insert_query.prepare(
            "INSERT OR IGNORE INTO followed (userid,description,display_name, view_count) VALUES (?, ?, ?, ?)"
        )
        for d in followed_list:
            insert_query.addBindValue(d["id"])
            insert_query.addBindValue(d["description"])
            insert_query.addBindValue(d["display_name"])
            insert_query.addBindValue(d["view_count"])

            insert_query.exec_()

    @staticmethod
    def insert_token(token):
        insert_query = QSqlQuery()
        insert_query.prepare("INSERT OR REPLACE INTO auth (usertoken) VALUES (?)")
        insert_query.addBindValue(token)

        insert_query.exec_()

    def get_token(self):
        token_query = QSqlQuery("SELECT usertoken from auth")

        if token_query.exec_() and token_query.last():
            return token_query.value(0)
        return False
