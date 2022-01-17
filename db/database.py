import sys

from PySide2.QtSql import QSqlDatabase, QSqlQuery
from PySide2.QtWidgets import QMessageBox


class ItchificationDB:
    def __init__(self):
        self.dbconn = QSqlDatabase.addDatabase("QSQLITE")
        self.dbconn.setDatabaseName("itchification.sqlite")

        if not self.dbconn.open():
            QMessageBox.critical(None, "App Name - Error!",
                                 "Database Error: %s" % self.dbconn.lastError().databaseText())
            sys.exit(1)

        self.check_table_exists()

    # create 'tables' not 'table' token table with uniqye constrsaint on token field
    def create_tables(self):
        db = self.dbconn.database()
        create_followed_table = QSqlQuery(db)
        if not create_followed_table.exec_("""
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
        if not create_auth_table.exec_("""
                    CREATE TABLE IF NOT EXISTS auth (
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                        usertoken VARCHAR(60) NOT NULL,
                        UNIQUE(usertoken)
                    );
                    """
                                           ):
            print(self.dbconn.lastError().databaseText())

    def check_table_exists(self):
        print(self.dbconn.tables())
        if 'auth' in self.dbconn.tables():
            return
        QMessageBox.critical(None, "Tables Query Error!", "Tables Not There:")
        self.create_tables()

    @staticmethod
    def insert_followed(followed_list):
        insert_query = QSqlQuery()

        insert_query.prepare("INSERT OR IGNORE INTO followed (userid,description,display_name, view_count) VALUES (?, ?, ?, ?)")
        for d in followed_list:
            insert_query.addBindValue(d['id'])
            insert_query.addBindValue(d['description'])
            insert_query.addBindValue(d['display_name'])
            insert_query.addBindValue(d['view_count'])

            insert_query.exec_()
