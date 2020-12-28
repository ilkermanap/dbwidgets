"""
This module provides a database object, and a set of widgets that makes
use of this database object.

"""

import psycopg2
import sqlite3
import traceback as tb


class Column:
    """This class represents a column in a table.

    Attributes
    ----------

    name : str
        Name of the column

    datatype : str
        Data type of the column

    default : Variable
        Default value for the column, default is None

    primary_key : Boolean
        True if the column is primary key

    foreign_key_table : str
        Name of the foreign key table

    foreign_key_column : str
        Name of the column that is set as foreign key.

    foreign_key_join_column : str
        Name of the column to use when querying the table.

    join_type : str
        Type of the join to use when querying the table. Either INNER or OUTER.


    """

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
        """Set primary_key value to True, making this column a primary key.

        """
        self.primary_key = True

    def addForeignKey(self, tablename, columnname, join_column=None, join_type="INNER"):
        """Set this column as foreign key. Currently we can't extract
        the join column from database.

        Parameters
        ----------
        tablename : str
            Other table's name

        columnname : str
            Column name in other table

        join_column : str, optional
            Column name to use for constructing the query to include
            the column from the other table

        join_type : str, optional
            Join type for the query, either INNER or OUTER

        """
        self.foreign_key_table = tablename
        self.foreign_key_column = columnname
        if join_column is not None:
            self.foreign_key_join_column = join_column
            self.join_type = join_type

    def setJoinColumn(self, join_column, join_type="INNER"):
        """Set join column for foreign key.

        Parameters
        ----------
        join_column : str
            Column name to use for constructing the query to include
            the column from the other table

        join_type : str
             Join type for the query, either INNER or OUTER

        """
        if self.foreign_key_table is None:
            raise Exception(f"No foreign key defined for this column : {self.name}. Can't set join column")
        self.foreign_key_join_column = join_column

        self.join_type = join_type

    def __str__(self):
        pkey = ""
        if self.primary_key is True:
            pkey = "primary key"
        if self.foreign_key_table is not None:
            return f"{self.name}  {self.datatype} {pkey} fkey:  {self.foreign_key_table}/{self.foreign_key_column} "

        return f"{self.name}  {self.datatype} {pkey}"


class Table:
    """This class represents a database table.

    These classes are constructed automatically by DB class.

    Attributes
    ----------

    name : str
        Name of the table

    columns : dict
        Columns of the table as a dict. Column name as key values.

    """

    def __init__(self, tablename):
        """
        Parameters
        ----------
        tablename : str
            Name of the table.

        """
        self.name = tablename
        self.columns = {}

    def addColumn(self, column):
        """
        Parameters
        ----------
        column : Column
            (Column) Add a column object to table. Parameter must be a Column object
            This method is not called directly. It is called from DB class when
            extracting the database schema automatically.

        """
        self.columns[column.name] = column

    def freeform_query(self, cursor, query_string):
        """
        Execute a freeform query given by query_string, using the cursor provided.

        Parameters
        ----------
        cursor : database cursor
            Cursor to execute the query

        query_string : str
            Query to execute

        Returns
        -------
        list : list
            List of records

        """
        cursor.execute(querystr)
        return cursor.fetchall()

    def query(self, cur, condition=None):
        """
        Execute a query, using the cursor provided. Default query is

            SELECT * FROM tablename

        If a condition is given, it will be added at the end of the query.
        Default query with condition must provide a valid sql sentence.

        Parameters
        ----------
        cursor : database cursor
            Cursor to execute the query

        condition : str or None
            Conditions to append to the end of the query.

        Returns
        -------
        List of records : list
            List of records

        """
        if condition is not None:
            cur.execute(f"select * from {self.name} {condition}")
        else:
            cur.execute(f"select * from {self.name}")
        return cur.fetchall()

    def tbprint(self):
        """Print a report of the table, lists column descriptions.

        """
        print(f"<{self.name}>")
        for col in self.columns.values():
            print("   ", col)
        print("-" * 30)


class DB:
    """
    This class represents the base Database class. New classes for
    individual databases like sqlite or postgresql inherits this class.


    Attributes
    ----------
    host : str
        Host name of the server that database is running. None for SQLite. Default is None

    port : int
        Port number for the database service. None for SQLite. Default is None

    dbname : str
        Name of the database

    tables : dict
        Dictionary of tables in the database. Key value is table name.

    connection : Connection handle
        Connection handle to database.

    filename : str
        Name of the database file. Valid for SQLite. Default is None

    """

    def __init__(self, host=None, port=None, dbname=None, filename=None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.tables = {}
        self.connection = None
        self.filename = filename

    def report(self):
        """
        Print the extracted database schema to standart output

        """
        print(f"DATABASE {self.dbname} ")
        for tb in self.tables.values():
            tb.tbprint()

    def execute(self, query_string):
        """
        Execute a query given by query_string, using the cursor provided.

        Parameters
        ----------
        query_string : str
            Query to execute

        Returns
        -------
        List of records : list
            List of records

        """

        cur = self.connection.cursor()
        try:
            cur.execute(query_string)
            return cur.fetchall()
        except:
            tb.print_exc()
            print("Cannot execute ", query_string)
            return None

    def record(self, tablename, pkey_column, pkey_value):
        """
        Retrieve a record from given tablename, using given primary key column and value.


            SELECT * FROM tablename WHERE pkey_column = pkey_value


        Parameters
        ----------
        tablename : str
            Name of the table

        pkey_column : str
            Name of the primary key column

        pkey_value : variable
            Value for the pkey_column

        Returns
        -------
        Record : list
            Returns a row from table.

        """

        if tablename in self.tables.keys():
            cur = self.connection.cursor()
            records = self.tables[tablename].query(cur, f" where {pkey_column}={pkey_value}")
            _record = None
            if records is not None:
                _record = records[0]
            return _record


class DBSQLite(DB):
    """
    This class represents the SQLite database class.

    Attributes
    ----------

    filename : str
        Name of the SQLite database file.

    connection : Connection handle
        Connection handle to database.

    """

    def __init__(self, filename):
        DB.__init__(self, filename=filename)
        self.connection = sqlite3.connect(self.filename)

    def extract(self):
        """
        Extracts table schema from sqlite internal tables: pragma_table_info and pragma_foreign_key_list.

        Fills self.tables dictionary.

        """
        tablenames = self.execute("select name from sqlite_master")

        for table in tablenames:
            t = Table(table[0])
            columns = self.execute(f"select * from pragma_table_info('{table[0]}')")
            fkeys = self.execute(f"SELECT * FROM pragma_foreign_key_list('{table[0]}')")
            for col in columns:
                colname = col[1]
                coltype = col[2]
                pkey = False
                if col[5] == 1:
                    pkey = True
                t.addColumn(Column(colname, coltype, primary_key=pkey))
            if fkeys is not None:
                for fk in fkeys:
                    tbname = fk[2]
                    from_col = fk[3]
                    to_col = fk[4]
                    t.columns[from_col].addForeignKey(tbname, to_col)
            self.tables[table[0]] = t


class DBPostgres(DB):
    """
    This class represents the Postgresql database class.

    Attributes
    ----------
    host : str
        Host name of the server that database is running. Default is None

    port : int
        Port number for the database service. Default is None

    dbname : str
        Name of the database

    tables : dict
        Dictionary of tables in the database. Key value is table name.

    connection : Connection handle
        Connection handle to database.


    """

    def __init__(self, host=None, port=None, dbname=None, username=None, password=None, filename=None):
        # TODO: Add support for connecting through unix socket
        DB.__init__(self, host=host, port=port, dbname=dbname, filename=filename)

        self.connection = None
        self.connected = False
        if (username is not None):
            self.connect(username, password)
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
        """
        Extracts table schema from postgresql internal tables.

        Fills self.tables dictionary.

        """
        tablenames = self.execute("select table_name from information_schema.tables where table_schema='public'")
        columns = self.execute(
            "select table_name, column_name, data_type, column_default from information_schema.columns where table_schema='public'")
        primary_keys = self.execute("""SELECT 
                        c.column_name, c.table_name 
                    FROM 
                        information_schema.key_column_usage AS c 
                    LEFT JOIN 
                        information_schema.table_constraints AS t ON t.constraint_name = c.constraint_name 
                    WHERE  
                        t.constraint_type = 'PRIMARY KEY'""")
        foreign_keys = self.execute("""SELECT
                    tc.table_name, kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                 FROM
                    information_schema.table_constraints AS tc
                 JOIN 
                    information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
                 JOIN 
                    information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
                 WHERE 
                    constraint_type = 'FOREIGN KEY';""")

        for table in tablenames:
            t = Table(table[0])
            for col in columns:
                if col[0] == table[0]:
                    t.addColumn(Column(col[1], col[2], default=col[3]))
            self.tables[table[0]] = t

        for pkey_column, tablename in primary_keys:
            self.tables[tablename].columns[pkey_column].setPrimary()

        for tablename, column, fktablename, fkcolumn in foreign_keys:
            self.tables[tablename].columns[column].addForeignKey(fktablename, fkcolumn)


if __name__ == "__main__":
    db = DBSQLite("test.db")
    db.extract()
    db.report()
