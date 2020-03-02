############
Introduction
############

Dbwidgets module has two group of classes.

* Database Classes
* GUI Classes


################
Database Classes
################

First group is for database abstraction. We are generating a database model
which includes tables and columns, and also primary key and foreign key
information from database's internal tables.  These information is held in a
DB class, which later used by ui components.

By providing same object representation of different databases, ui part becomes
database vendor agnostic.

Currently, SQLite and Postgresql databases are implemented.

DB
==

.. autoclass:: dbwidgets.DB
   :members:

Example
-------

.. code-block:: python

    from dbwidgets import DBSQLite

    db = DBSQLite("test.db")
    db.extract()

    customer = db.record("customers", "id", 123)


Table
=====

.. autoclass:: dbwidgets.Table
   :members:


Column
======

.. autoclass:: dbwidgets.Column
   :members:


###########
GUI Classes
###########

DBCombobox
==========

.. autoclass:: dbwidgets.widgets.DBComboBox
   :members:

DBNavigatorWidget
=================

.. autoclass:: dbwidgets.widgets.DBNavigatorWidget
   :members:

DBTableWidget
=============

.. autoclass:: dbwidgets.widgets.DBTableWidget
   :members:


Example
=======

In the example below, the database has two tables: city and district:

.. code-block:: sql

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

City and district tables are connected with one to many relationship. One city has many districts.

.. code-block:: python
    :linenos:

    import  sys
    from dbwidgets import DBSQLite
    from dbwidgets.widgets import DBComboBox, DBTableWidget, DBNavigatorWidget
    from PySide2.QtWidgets import QApplication, QDialog
    from ui_test import Ui_Dialog

    class MainWindow(QDialog, Ui_Dialog):
        def __init__(self, app=None):
            super(MainWindow, self).__init__()
            self.app = app
            self.db = DBSQLite("test.db")
            self.db.extract()
            self.setupUi(self)
            self.city = DBComboBox(self.widget1, self.db, "city", "name", "id", 34)
            self.district = DBComboBox(self.widget2, self.db, "district", "name", "id")
            self.district.setMaster(self.city, "city_id")
            self.districtlist = DBTableWidget(self.widget3, self.db, "district")
            self.districtlist.setMaster(self.city, "city_id")
            self.citylist = DBTableWidget(self.widget4, self.db, "city")
            self.districtlist.setMaster(self.citylist, "city_id")
            self.show()

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        mainWin = MainWindow(app)
        ret = app.exec_()
        app.exit()
        sys.exit(ret)


* Line 11, we  create the database object by giving connection parameters. For sqlite, file name is sufficient.
* Line 12, call extract() to create the table objects inside database object.
* Line 14, place combobox widget for city table. Here, self.widget1 is the placeholder on ui definition. self.db is the database, "city" is the name of the table, "name" is the column for displaying inside combobox. 34 is the optional default value of the primary key for the combobox to display first.
* Line 15, place the combobox for "district" table. Similar parameters as above.
* Line 16, now we will create a master detail connection between these two comboboxes. We will call detail table's setMaster method. self.city is the widget to use as master, "city_id" is the column name on the detail table, in our example, "district" table's "city_id" column.


With three lines, we have two comboboxes connected with master-detail relationship.


* Line 17 for creating a DBTableWidget for "district" table.
* Line 18 to connect "district" dbtablewidget to city combobox
* Line 19 to create a dbtablewidget for "city" table.
* Line 20 to connect "district" dbtablewidget to "city" dbtablewidget
