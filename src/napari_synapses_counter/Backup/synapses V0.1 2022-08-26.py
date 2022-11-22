import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, \
    QPushButton, QRadioButton, QCheckBox, QLineEdit, QComboBox, \
    QHBoxLayout, QVBoxLayout, QGridLayout, QButtonGroup


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Analyze synapses")
        widget = QWidget()

        # Definition of the required layouts
        page_layout = QVBoxLayout()
        grid1 = QGridLayout()
        grid2 = QGridLayout()
        label_layout = QHBoxLayout()
        grid3 = QGridLayout()
        grid4 = QGridLayout()
        grid5 = QGridLayout()

        # Arange the layouts
        page_layout.addLayout(grid1)
        page_layout.addLayout(grid2)
        page_layout.addLayout(label_layout)
        page_layout.addLayout(grid3)
        page_layout.addLayout(grid4)
        page_layout.addLayout(grid5)

        # Place the widgets within the layouts
        # 1st Input_source
        label1 = QLabel('Choose input source:')
        radio_button1 = QRadioButton('current image')
        radio_button2 = QRadioButton('batch mode')
        button_group1 = QButtonGroup(widget)
        button_group1.addButton(radio_button1)
        button_group1.addButton(radio_button2)

        # 2nd Input dimensionality
        label2 = QLabel('Input dimensionality:')
        radio_button3 = QRadioButton('2D')
        radio_button4 = QRadioButton('3D')
        button_group2 = QButtonGroup(widget)
        button_group2.addButton(radio_button3)
        button_group2.addButton(radio_button4)

        grid1.addWidget(label1, 0, 0)
        grid1.addWidget(radio_button1, 0, 1)
        grid1.addWidget(radio_button2, 0, 2)
        grid1.addWidget(label2, 1, 0)
        grid1.addWidget(radio_button3, 1, 1)
        grid1.addWidget(radio_button4, 1, 2)

        # 3rd Input and output files
        button1 = QPushButton('Input folder')
        line1 = QLineEdit()
        check_box1 = QCheckBox('search in subfolders')
        check_box2 = QCheckBox('save intermediate files')
        button2 = QPushButton('OutputFolder')
        line2 = QLineEdit()

        grid2.addWidget(button1, 0, 0)
        grid2.addWidget(line1, 0, 1)
        grid2.addWidget(check_box1, 1, 0)
        grid2.addWidget(check_box2, 2, 0)
        grid2.addWidget(button2, 3, 0)
        grid2.addWidget(line2, 3, 1)

        # 4th Label
        label3 = QLabel('Analysis settings:')
        label_layout.addWidget(label3)

        # 5th Some input parameters
        label4 = QLabel('Image type:')
        c_box1 = QComboBox()
        c_box1.addItems(['RGB', 'CMYK', 'HSV', 'B/W', 'gray scale'])

        label5 = QLabel('Presynaptic protein channel:')
        c_box2 = QComboBox()
        c_box2.addItems(['red', 'yellow', 'green', 'cyan', 'blue', 'magenta'])

        label6 = QLabel('Postsynaptic protein channel:')
        c_box3 = QComboBox()
        c_box3.addItems(['red', 'yellow', 'green', 'cyan', 'blue', 'magenta'])
        c_box3.setCurrentIndex(2)       # the default value is 'green'

        label7 = QLabel('Resize image width: [px]')
        line3 = QLineEdit('1024')

        label8 = QLabel('Rolling ball radius:')
        line4 = QLineEdit('10.0')

        label9 = QLabel('Maximum filter radius:')
        line5 = QLineEdit('1.0')

        label10 = QLabel('Method of threshold adjustment:')
        c_box4 = QComboBox()
        c_box4.addItems(['Otsu', 'ASDF', 'JKLÖ'])

        grid3.addWidget(label4, 0, 0)
        grid3.addWidget(c_box1, 0, 1)
        grid3.addWidget(label5, 1, 0)
        grid3.addWidget(c_box2, 1, 1)
        grid3.addWidget(label6, 2, 0)
        grid3.addWidget(c_box3, 2, 1)
        grid3.addWidget(label7, 3, 0)
        grid3.addWidget(line3,  3, 1)
        grid3.addWidget(label8, 4, 0)
        grid3.addWidget(line4,  4, 1)
        grid3.addWidget(label9, 5, 0)
        grid3.addWidget(line5,  5, 1)
        grid3.addWidget(label10, 6, 0)
        grid3.addWidget(c_box4,  6, 1)

        #6th Min. and max. particle size
        label11 = QLabel('Presynaptic particle size')
        line6 = QLineEdit('20')
        label12 = QLabel('px² or voxels')

        label13 = QLabel('Max. presynaptic particle size')
        line7 = QLineEdit('1200')
        label14 = QLabel('px² or voxels')

        label15 = QLabel('Min. presynaptic particle size')
        line8 = QLineEdit('15')
        label16 = QLabel('px² or voxels')

        label17 = QLabel('Max. Postsynaptic particle size')
        line9 = QLineEdit('1200')
        label18 = QLabel('px² or voxels')

        grid4.addWidget(label11, 0, 0)
        grid4.addWidget(line6,   0, 1)
        grid4.addWidget(label12, 0, 2)
        grid4.addWidget(label13, 1, 0)
        grid4.addWidget(line7,   1, 1)
        grid4.addWidget(label14, 1, 2)
        grid4.addWidget(label15, 2, 0)
        grid4.addWidget(line8,   2, 1)
        grid4.addWidget(label16, 2, 2)
        grid4.addWidget(label17, 3, 0)
        grid4.addWidget(line9,   3, 1)
        grid4.addWidget(label18, 3, 2)

        # 6th Buttons
        button3 = QPushButton('Reset to default')
        button4 = QPushButton('OK')
        button5 = QPushButton('Cancel')
        button6 = QPushButton('Help')

        grid5.addWidget(button3, 0, 0)
        grid5.addWidget(button4, 1, 1)
        grid5.addWidget(button5, 1, 2)
        grid5.addWidget(button6, 1, 3)

        widget.setLayout(page_layout)
        self.setCentralWidget(widget)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
