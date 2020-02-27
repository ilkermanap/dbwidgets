import psycopg2
import sqlite3
import traceback as tb



class Column:
    def __init__(self, name, datatype, primary_key=False, default=None):
        self.name = name
        self.datatype = datatype
        self.default = default
        self.primary_key = primary_key
        self.foreign_key_table = None
        self.foreign_key_column = None
        self.foreign_key_join_column = None
        self.join_type = None

    def setPrimary(self):
        self.primary_key = True
        
    def addForeignKey(self, tablename, columnname, join_column=None, join_type="INNER"):
        self.foreign_key_table = tablename
        self.foreign_key_column = columnname
        if join_column is not None:
            self.foreign_key_join_column = join_column
            # if not given explicitly, default join type is INNER
            self.join_type = join_type

    def setJoinColumn(self, join_column, join_type="INNER"):
        if self.foreign_key_table is None:
            raise Exception(f"No foreign key defined for this column : {self.name}. Can't set join column")
        self.foreign_key_join_column = join_column
        # if not given explicitly, default join type is INNER
        self.join_type = join_type
                                       
    def __str__(self):
        pkey = ""
        if self.primary_key is True:
            pkey ="primary key"
        if self.foreign_key_table is not None:
            return f"{self.name}  {self.datatype} {pkey} fkey:  {self.foreign_key_table}/{self.foreign_key_column} "

        return f"{self.name}  {self.datatype} {pkey}"

    
class Table:
    def __init__(self, tablename):
        self.name = tablename
        self.columns = {}
    
    def addColumn(self, column):
        self.columns[column.name] = column 

    def freeform_query(self, cur, querystr):
        cur.execute(querystr)
        return cur.fetchall()
        
    def query(self, cur, condition=None):
        if condition is not None:
            cur.execute(f"select * from {self.name} {condition}")
        else:
            cur.execute(f"select * from {self.name}")
        return cur.fetchall()

    def tbprint(self):
        print(f"<{self.name}>")
        for col in self.columns.values():
            print("   ", col)
        print("-"*30)

class DB:
    def __init__(self, host=None, port=None, dbname=None, filename=None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.tables = {}
        self.connection = None
        self.filename = filename

    def report(self):
        print(f"DATABASE {self.dbname} ")
        for tb in self.tables.values():
            tb.tbprint()

    def execute(self, querystr):
        cur = self.connection.cursor()
        try:
            cur.execute(querystr)
            return  cur.fetchall()
        except:
            tb.print_exc()
            print("Cannot execute ", querystr)
            return None

    def record(self, tablename, pkey_column, pkey_value):
        if tablename in self.tables.keys():
            cur = self.connection.cursor()
            rec = self.tables[tablename].query(cur, f" where {pkey_column}={pkey_value}")
            if rec is not None:
                rec = rec[0]
            return rec


            
class DBSQLite(DB):
    def __init__(self, fname):
        DB.__init__(self, filename=fname)
        self.connection = sqlite3.connect(self.filename)

    def extract(self):
        tablenames = self.execute("select name from sqlite_master")
        
        for table  in tablenames:
            t = Table(table[0])
            columns = self.execute(f"select * from pragma_table_info('{table[0]}')")
            fkeys = self.execute(f"SELECT * FROM pragma_foreign_key_list('{table[0]}')")
            for col in columns:
                colname = col[1]
                coltype = col[2]
                pkey = False
                if col[5] == 1:
                    pkey=True
                t.addColumn(Column(colname, coltype, primary_key=pkey))
            if fkeys is not None:
                for fk in fkeys:
                    tbname = fk[2]
                    from_col = fk[3]
                    to_col = fk[4]
                    t.columns[from_col].addForeignKey(tbname, to_col)
            self.tables[table[0]]  =  t
                                               

class DBPostgres(DB):
    def __init__(self, host=None, port=None, dbname=None, username =None, password = None, filename=None):
        DB.__init__(self,host=host, port=port, dbname=dbname, filename=filename)
 
        self.connection = None
        self.connected = False
        if (username is not None):
            self.connect()
        if self.connected:
            self.extract()
        
    def connect(self, user, passwd):
        conn_str = f"dbname='{self.dbname}' user='{user}' host='{self.host}' password='{passwd}' " 
        try:
            self.connection = psycopg2.connect(conn_str)
            if self.connection is not None:
                self.connected = True
        except psycopg2.OperationalError:
            tb.print_exc()
            self.connected = False


    def extract(self):
        tablenames = self.execute("select table_name from information_schema.tables where table_schema='public'")
        columns = self.execute("select table_name, column_name, data_type, column_default from information_schema.columns where table_schema='public'")
        primary_keys = self.execute("SELECT c.column_name, c.table_name FROM information_schema.key_column_usage AS c LEFT JOIN information_schema.table_constraints AS t ON t.constraint_name = c.constraint_name WHERE  t.constraint_type = 'PRIMARY KEY'")
        foreign_keys = self.execute("""SELECT
                   tc.table_name, kcu.column_name,
                   ccu.table_name AS foreign_table_name,
                   ccu.column_name AS foreign_column_name
                 FROM
                   information_schema.table_constraints AS tc
                 JOIN information_schema.key_column_usage 
                 AS kcu ON tc.constraint_name = kcu.constraint_name
                 JOIN information_schema.constraint_column_usage 
                 AS ccu ON ccu.constraint_name = tc.constraint_name
                 WHERE constraint_type = 'FOREIGN KEY';""")

        for table in tablenames:
            t = Table(table[0])
            for col in columns:
                if col[0] == table[0]:
                    t.addColumn(Column(col[1], col[2], default=col[3]))
            self.tables[table[0]] = t

        for pkey_column, tablename  in primary_keys:
            self.tables[tablename].columns[pkey_column].setPrimary()

        for tablename, column, fktablename, fkcolumn in foreign_keys:
            self.tables[tablename].columns[column].addForeignKey(fktablename, fkcolumn)
            

if __name__ == "__main__":
    db = DBSQLite("test.db")
    db.extract()
    db.report()
    


    
