import psycopg2
import conf


class DatabaseUploader:
    """For uploading the files in PostgresSQL"""
    def __init__(self):
        self.dbname = conf.db_name
        self.user = conf.db_username
        self.password = conf.db_password
        self.host = conf.db_host
        self.port = 5432
        self.conn = None

    def connect_to_database(self):
        self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password,
                                     host=self.host, port=self.port)
        return self.conn

    def close_connection(self):
        if self.conn:
            self.conn.close()