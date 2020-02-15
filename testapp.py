from dbmodel import DBSQLite
from dbmodel.widgets import DBComboBox, DBTableWidget, DBNavigatorWidget
import  sys

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

        self.citylist = DBTableWidget(self.widget3, self.db, "district")
        self.citylist.setMaster(self.city, "city_id")
        self.district_nav = DBNavigatorWidget(self.widget4, self.db, "district")

        self.show()
        
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow(app)
    ret = app.exec_()
    app.exit()
    sys.exit(ret)


    
