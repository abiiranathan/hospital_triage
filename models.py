import mysql.connector as mysql
from contextlib import closing

class Db(object):
    """docstring for PatientDB"""
    database_name = "patients"
    table_name = "triage"
    fields=[]

    def __init__(self):
        # self.connection = MySQLdb.connect(**config)
        self.connection = mysql.connect(host='localhost', user='root',
            password="cmaster2018", database=self.database_name)

    def insert(self, patient):
        keys = ",".join(patient.__dict__.keys())
        values = tuple(patient.__dict__.values())

        with closing(self.connection.cursor()) as cursor:
            try:
                sql = '''INSERT INTO {} ({}) VALUES('''.format(self.table_name, keys) + """ "%s",""" * len(values) % (values)
                sql = sql[:-1] + ")"
                cursor.execute(sql)
                self.connection.commit()
            except Exception as e:
                return str(e)
            else:
                return True

    def update(self, patient):
        sql = """UPDATE {} SET""".format(self.table_name)
        for key, value in patient.__dict__.items():
            sql += """ %s = "%s" ,""" % (key, value)
        sql = sql[:-1] + """ WHERE ID = "{}" """.format(patient.ID)

        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(sql)
                self.connection.commit()
                return True
            except Exception as e:
                raise

    def lookup(self, pk):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute("""SELECT * FROM {} WHERE ID = "{}" """.format(self.table_name, pk))
            rows = cursor.fetchall()
            self.fields=cursor.description
            return rows if rows else None

    def transaction(self):
        return self.connection

    def get_all(self):
        with closing(self.connection.cursor()) as cursor:
            cursor.execute("SELECT * FROM {}".format(self.table_name))
            rows = cursor.fetchall()
            self.fields=cursor.description
            return rows if rows else None

    def remove(self, pk):
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute("DELETE FROM {} WHERE ID='{}'".format(self.table_name, pk))
                self.connection.commit()
            except Exception as e:
                return str(e)
            return True

    def execute(self, sql):
        with closing(self.connection.cursor()) as cursor:
            try:
                cursor.execute(sql)
                self.fields=cursor.description
                return cursor.fetchall()
            except Exception as e:
               pass


