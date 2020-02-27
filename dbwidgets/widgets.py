from PySide2.QtWidgets import QComboBox, QTableWidget, QTableWidgetItem, QWidget
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtCore import Signal
from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

from . import *

class DBComboBox(QComboBox):

    signalMasterId = Signal(object)
    
    def __init__(self, parent,  db, tablename, textcolumn, idcolumn, default_id = None):
        super(DBComboBox, self).__init__(parent)
        self.table = tablename
        self.db = db
        self.textcolumn = textcolumn
        self.idcolumn = idcolumn
        self.mastercolumn = None                
        self.dataquery = f"select {idcolumn}, {textcolumn} from {self.table}"
        self.fill()
        self.selected_id = None
        self.currentIndexChanged.connect(self.idxChanged)

        if default_id is not None:
            i = 0
            found = False
            while ((i <= self.count()) or (found == False)):
                if self.itemData(i) == default_id:
                    found = True
                    self.setCurrentIndex(i)
                i+=1
                
    def refill(self,obj):
        self.clear()
        values = self.db.execute(self.dataquery + f" where {self.mastercolumn} = {obj} ")
        for id, text in values:        
            self.addItem(text, userData=id)

            
    def idxChanged(self):
        self.selected_id = self.itemData(self.currentIndex())
        self.signalMasterId.emit(self.itemData(self.currentIndex()))

                
    def fill(self):
        self.clear()
        values = self.db.execute(self.dataquery)
        for id, text in values:        
            self.addItem(text, userData=id)


    def setMaster(self, otherwidget, mycolumn_name):
        mycolumn = self.db.tables[self.table].columns[mycolumn_name]
        # check if requested connection is valid
        if ( mycolumn.foreign_key_table is None ):
            raise Exception(f"Requested connection between {self.table.name} and {otherwidget.table.name} cannot be made, no foreign key for {mycolumn_name} defined.")
        
        elif ( mycolumn.foreign_key_table != otherwidget.table):
            raise Exception(f"Requested connection between {self.table} and {otherwidget.table} cannot be made, wrong table name")

        elif ( mycolumn.foreign_key_table == otherwidget.table): # check existence of foreign key column
            if (mycolumn.foreign_key_column not in otherwidget.db.tables[otherwidget.table].columns.keys()):
                raise Exception(f"Foreign key column {mycolumn.foreign_key_column} not found in {otherwidget.table}")
            else: # everything looks ok, create the connection
                otherwidget.signalMasterId.connect(self.refill)
                self.mastercolumn = mycolumn_name
                self.refill(otherwidget.selected_id)
                
class DBNavigatorWidget(QWidget):

    def __init__(self, parent, db, tablename):
        super(DBNavigatorWidget, self).__init__(parent)
        self.db = db
        self.tablename = tablename
        self.setupUi(self)
        self.show()

    def setupUi(self, DBNavigatorWidget):
        if DBNavigatorWidget.objectName():
            DBNavigatorWidget.setObjectName(u"DBNavigatorWidget")

        self.verticalLayout = QVBoxLayout(DBNavigatorWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.dbeditWidget = QWidget(DBNavigatorWidget)
        self.dbeditWidget.setObjectName(u"dbeditWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbeditWidget.sizePolicy().hasHeightForWidth())
        self.dbeditWidget.setSizePolicy(sizePolicy)
        self.verticalLayout.addWidget(self.dbeditWidget)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.btnDBNavFirst = QPushButton(DBNavigatorWidget)
        self.btnDBNavFirst.setObjectName(u"btnDBNavFirst")
        self.horizontalLayout.addWidget(self.btnDBNavFirst)
        self.btnDBNavPrev = QPushButton(DBNavigatorWidget)
        self.btnDBNavPrev.setObjectName(u"btnDBNavPrev")
        self.horizontalLayout.addWidget(self.btnDBNavPrev)
        self.btnDBNavNext = QPushButton(DBNavigatorWidget)
        self.btnDBNavNext.setObjectName(u"btnDBNavNext")
        self.horizontalLayout.addWidget(self.btnDBNavNext)
        self.btnDBNavLast = QPushButton(DBNavigatorWidget)
        self.btnDBNavLast.setObjectName(u"btnDBNavLast")
        self.horizontalLayout.addWidget(self.btnDBNavLast)
        self.btnDBNavAdd = QPushButton(DBNavigatorWidget)
        self.btnDBNavAdd.setObjectName(u"btnDBNavAdd")
        self.horizontalLayout.addWidget(self.btnDBNavAdd)
        self.btnDBNavDelete = QPushButton(DBNavigatorWidget)
        self.btnDBNavDelete.setObjectName(u"btnDBNavDelete")
        self.horizontalLayout.addWidget(self.btnDBNavDelete)
        self.btnDBNavAccept = QPushButton(DBNavigatorWidget)
        self.btnDBNavAccept.setObjectName(u"btnDBNavAccept")
        self.horizontalLayout.addWidget(self.btnDBNavAccept)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.retranslateUi(DBNavigatorWidget)
        self.btnDBNavFirst.clicked.connect(DBNavigatorWidget.DBNavFirst)
        QMetaObject.connectSlotsByName(DBNavigatorWidget)
    # setupUi

    def retranslateUi(self, DBNavigatorWidget):
        DBNavigatorWidget.setWindowTitle(QCoreApplication.translate("DBNavigatorWidget", u"Form", None))
        self.btnDBNavFirst.setText(QCoreApplication.translate("DBNavigatorWidget", u"<<", None))
        self.btnDBNavPrev.setText(QCoreApplication.translate("DBNavigatorWidget", u"<", None))
        self.btnDBNavNext.setText(QCoreApplication.translate("DBNavigatorWidget", u">", None))
        self.btnDBNavLast.setText(QCoreApplication.translate("DBNavigatorWidget", u">>", None))
        self.btnDBNavAdd.setText(QCoreApplication.translate("DBNavigatorWidget", u"+", None))
        self.btnDBNavDelete.setText(QCoreApplication.translate("DBNavigatorWidget", u"-", None))
        self.btnDBNavAccept.setText(QCoreApplication.translate("DBNavigatorWidget", u"Ok", None))
    # retranslateUi

    def DBNavFirst(self):
        pass

    def DBNavPrev(self):
        pass

    def DBNavLast(self):
        pass

    def DBNavNext(self):
        pass

    def DBNavNew(self):
        pass

    def DBNavDelete(self):
        pass

    def DBNavAccept(self):
        pass



class DBTableWidget(QTableWidget):

    signalCellChange = Signal(object)
    signalMasterId = Signal(object)
    signalRowChanged = Signal(object)

    def __init__(self, parent,  db, tablename, default_id = None, ):
        super(DBTableWidget,self).__init__(parent)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.current_row = None
        self.selected_id = None
        self.db = db
        self.setFixedWidth(parent.width())
        self.table = tablename
        """
        SELECT Orders.OrderID, Customers.CustomerName, Orders.OrderDate
        FROM Orders
        INNER JOIN Customers ON Orders.CustomerID=Customers.CustomerID; 
        """

        self.dataquery = f"select  * from {self.table}"
        self.clear()
        self.current_id = None

        records = self.db.execute(self.dataquery)
        self.setRowCount(len(records))
        self.setColumnCount(len(self.db.tables[self.table].columns.keys()))

        self.setHorizontalHeaderLabels( self.db.tables[self.table].columns.keys())
        i=0
        for record in records:
            j=0
            for k in record:
                self.setItem(i, j,QTableWidgetItem( str(k)))                              
                j+=1
            i+=1
        self.cellClicked.connect(self.check_row)
        self.selected_id = int(self.itemAt(0,0).text())
        self.current_row = 0
        #self.itemChanged.connect(self.cellChanged)

    def check_row(self, x,y):
        if x != self.current_row:
            self.signalRowChanged.emit(int(self.item(x,0).text()))
            self.selected_id = int(self.item(x,0).text())
            self.current_row = int(self.item(x,0).text())



    def refill(self,obj):
        self.clear()
        records = self.db.execute(self.dataquery + f" where {self.mastercolumn} = {obj} ")
        self.setRowCount(len(records))

        i=0
        for record in records:
            j=0
            for k in record:
                self.setItem(i, j,QTableWidgetItem( str(k)))                              
                j+=1
            i+=1
                
    def cellChanged(self):
        print(self.currentRow(), self.currentColumn(), self.currentItem().text())
        pass                

    
    def setMaster(self, otherwidget, mycolumn_name, other_table_column_to_display=None):
        mycolumn = self.db.tables[self.table].columns[mycolumn_name]
        # check if requested connection is valid
        if ( mycolumn.foreign_key_table is None ):
            raise Exception(f"Requested connection between {self.table.name} and {otherwidget.table.name} cannot be made, no foreign key for {mycolumn_name} defined.")
        
        elif ( mycolumn.foreign_key_table != otherwidget.table):
            raise Exception(f"Requested connection between {self.table} and {otherwidget.table} cannot be made, wrong table name")

        elif ( mycolumn.foreign_key_table == otherwidget.table): # check existence of foreign key column
            if (mycolumn.foreign_key_column not in otherwidget.db.tables[otherwidget.table].columns.keys()):
                raise Exception(f"Foreign key column {mycolumn.foreign_key_column} not found in {otherwidget.table}")
            else: # everything looks ok, create the connection
                tp = type(otherwidget)
                
                if  tp  is DBComboBox:
                    otherwidget.signalMasterId.connect(self.refill)
                if tp is DBTableWidget:                    
                    otherwidget.signalRowChanged.connect(self.refill)
                self.mastercolumn = mycolumn_name
                self.refill(otherwidget.selected_id)


