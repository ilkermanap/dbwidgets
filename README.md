# dbmodel

Creates an object representation of given database. Aim is to generate data aware pyside2 widgets with master detail relationships defined automatically from database definitions. No gui widget generation implemented yet.

Postgresql and SQLite  databases are implemented.

Extracts column information, primary keys, and foreign keys if exists.


    db = DBSQLite("test.db")
    db.extract()


From that point, db has dictionary of tables, table names being the key value.
A table has a dictionary of columns, column names being the key value.

If a foreign key is defined for any column, the referring table name is foreign_key_table, referring column name is foreign_key_column as attributes for column object.


