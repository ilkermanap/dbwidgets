# dbmodel

Creates an object representation of given database. Aim is to generate data aware pyside2 widgets with master detail relationships defined automatically from database definitions. No gui widget generation implemented yet.

Postgresql and SQLite  databases are implemented.

Extracts column information, primary keys, and foreign keys if exists.


    db = DBSQLite("test.db")
    db.extract()


From that point, db has dictionary of tables, table names being the key value.
A table has a dictionary of columns, column names being the key value.

If a foreign key is defined for any column, the referring table name is foreign_key_table, referring column name is foreign_key_column as attributes for column object.

## Schema of the test database

    CREATE TABLE city (
	   id INTEGER NOT NULL, 
	   name VARCHAR, 
	   PRIMARY KEY (id)
    );

    CREATE TABLE district (
	   id INTEGER NOT NULL, 
	   name VARCHAR, 
	   city_id INTEGER, 
	   PRIMARY KEY (id), 
	   FOREIGN KEY(city_id) REFERENCES city (id)
    );

## Line By Line 

The lines below are from  testapp.py MainWindow __init__ section:

First, create the database object by giving connection parameters. 
For sqlite, file name is sufficient. 

    self.db = DBSQLite("test.db")
    
To create the table objects inside database object, call extract()

    self.db.extract()

Place combobox widget for city table. Here, self.widget1 is the placeholder on ui definition.
self.db is the database, "city" is the name of the table, "name" is the column for displaying inside combobox. 

    self.city = DBComboBox(self.widget1, self.db, "city", "name", "id", 34)

Place the combobox for "district" table. Similar parameters as above.
     
    self.district = DBComboBox(self.widget2, self.db, "district", "name", "id")

Now we will create a master detail connection between these two comboboxes.
We will call detail table's setMaster method. self.city is the widget to use as master, 
"city_id" is the column name on the detail table, in our example, "district" table's "city_id" column. 

    self.district.setMaster(self.city, "city_id")

With three lines, we have two comboboxes connected with master-detail relationship.

Below is the line for creating a DBTableWidget for "district" table.

    self.districtlist = DBTableWidget(self.widget3, self.db, "district")

This line connects "district" dbtablewidget to city combobox:

    self.districtlist.setMaster(self.city, "city_id")
    
This line will create a dbtablewidget for "city" table.

    self.citylist = DBTableWidget(self.widget4, self.db, "city")

This line connects "district" dbtablewidget to "city" dbtablewidget:
    
    self.districtlist.setMaster(self.citylist, "city_id")   
    
## Demo
![video](testapp.mp4)
