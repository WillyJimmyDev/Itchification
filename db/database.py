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

    def create_table(self):
        db = self.dbconn.database()
        create_table_query = QSqlQuery(db)
        print('creating table')
        if not create_table_query.exec_("""
            CREATE TABLE followed (
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
        else:
            print('created table')

    def check_table_exists(self):
        print(self.dbconn.tables())
        if 'followed' in self.dbconn.tables():
            return
        else:
            QMessageBox.critical(None, "Table Query Error!", "Table Not There:")
            self.create_table()

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
