from util.manager.student_manager import StudentManager
import typing

from PyQt5.QtCore import QThread, pyqtSignal, QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QColor

class StudentDataWorker(QThread):
    finishSignal = pyqtSignal(int)

    def __init__(self, manager : StudentManager, dataSet):
        super(StudentDataWorker, self).__init__()
        self.manager = manager
        self.dataSet = dataSet

    def run(self) -> None:

        self.dataSet = self.manager.getStudents(True)
        # emit the signal for notify thread work is done
        self.finishSignal.emit(len(self.dataSet))



class StudentModel(QAbstractTableModel):

    studentManager = None
    # load the data set of students using student manager engine
    _dataSet : list[dict] = None

    def __init__(self, connection, logger):
        super(StudentModel, self).__init__()
        StudentModel.studentManager = StudentManager(connection, logger)
        # load the data set in another thread
        # dataWorker = StudentDataWorker(self.studentManager, StudentModel._dataSet)
        # dataWorker.start()
        StudentModel._dataSet = self.studentManager.getStudents(True)

        try:
            self.fields = list(self._dataSet[0].keys())
        except:
            pass


    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:

        field = self.fields[index.column()]
        if role == Qt.DisplayRole:

            if field == "Password":
                return None
            elif  field == "Registered At" or field == "Birthday":
                return  StudentModel._dataSet[index.row()][field].strftime("%Y-%m-%d")

            return list(StudentModel._dataSet[index.row()].values())[index.column()]

        elif role == Qt.BackgroundRole:
            if field == "Password":
                return QColor.fromRgb(0, 0, 0)
            elif field == "Sex":
                gender = StudentModel._dataSet[index.row()][field]
                if gender == "male":
                    return QColor(0, 0, 255)
                elif gender == "female":
                    return QColor(255, 200, 0)
                else:
                    return QColor(0, 255, 0)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.fields[section]
        else:
            return None

    def rowCount(self, parent: QModelIndex = ...) -> int:

        return len(self._dataSet)

    def columnCount(self, parent: QModelIndex = ...) -> int:

        return len(self._dataSet[0].keys())