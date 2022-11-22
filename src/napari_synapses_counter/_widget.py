import sys
from qtpy.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, \
    QPushButton, QRadioButton, QCheckBox, QLineEdit, QComboBox, \
    QVBoxLayout, QGridLayout, QButtonGroup, QScrollArea, QFileDialog, \
    QMessageBox
from qtpy.QtCore import Qt
from tifffile import imread


class SynapsesCounter(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        widget1 = QWidget()

        # definition of the required layouts
        vbox1 = QVBoxLayout()
        grid1 = QGridLayout()
        grid2 = QGridLayout()
        grid3 = QGridLayout()
        grid4 = QGridLayout()

        # arange the layouts
        vbox1.addLayout(grid1)
        vbox1.addLayout(grid2)
        vbox1.addLayout(grid3)
        vbox1.addLayout(grid4)

        # input source
        self.rb_doOpenedImageButton = QRadioButton('current image')
        self.rb_doOpenedImageButton.setChecked(True)
        self.rb_doOpenedImageButton.clicked.connect(self.current_image)
        self.rb_doBatchButton = QRadioButton('batch mode')
        self.rb_doBatchButton.clicked.connect(self.batch_mode)

        # input dimensionality
        self.rb_is2dButton = QRadioButton('2D')
        self.rb_is2dButton.setChecked(True)
        self.rb_is3dButton = QRadioButton('3D')

        # define button groups
        bg_inputBox = QButtonGroup(widget1)
        bg_inputBox.addButton(self.rb_doOpenedImageButton)
        bg_inputBox.addButton(self.rb_doBatchButton)
        bg_dimBox = QButtonGroup(widget1)
        bg_dimBox.addButton(self.rb_is2dButton)
        bg_dimBox.addButton(self.rb_is3dButton)

        # place the widgets within the 1st grid
        grid1.addWidget(QLabel('Choose input source:'),  0, 0)
        grid1.addWidget(self.rb_doOpenedImageButton,     0, 1)
        grid1.addWidget(self.rb_doBatchButton,           0, 2)
        grid1.addWidget(QLabel('Input dimensionality:'), 1, 0)
        grid1.addWidget(self.rb_is2dButton,              1, 1)
        grid1.addWidget(self.rb_is3dButton,              1, 2)

        # input and output files
        self.pb_inputButton = QPushButton('Input folder')
        self.pb_inputButton.clicked.connect(self.input_folder)
        self.pb_inputButton.setEnabled(False)
        self.lb_inputDirField = QLabel()

        self.xb_doSubFoldersButton = QCheckBox('search in subfolders')
        self.xb_doSubFoldersButton.setChecked(False)
        self.xb_doOutputButton = QCheckBox('save intermediate files')
        self.xb_doOutputButton.setChecked(False)
        self.xb_doOutputButton.clicked.connect(self.save_intermediate_files)

        self.pb_outputButton = QPushButton('OutputFolder')
        self.pb_outputButton.clicked.connect(self.output_folder)
        self.pb_outputButton.setEnabled(False)
        self.lb_outputDirField = QLabel()

        # place the widgets within the 2nd grid
        grid2.addWidget(self.pb_inputButton,         0, 0)
        grid2.addWidget(self.lb_inputDirField,       0, 1)
        grid2.addWidget(self.xb_doSubFoldersButton,  1, 0)
        grid2.addWidget(self.xb_doOutputButton,      2, 0)
        grid2.addWidget(self.pb_outputButton,        3, 0)
        grid2.addWidget(self.lb_outputDirField,      3, 1)

        # Analysis settings
        # first column: labels
        label = QLabel('Analysis settings:')
        grid3.addWidget(label, 0, 0, alignment=Qt.AlignCenter)
        row = 1

        for str1 in [
            'Image type:',
            'Presynaptic protein channel:',
            'Postsynaptic protein channel:',
            'Resize image width:',
            'Rolling ball radius:',
            'Maximum filter radius:',
            'Method of threshold adjustment:',
            'Presynaptic particle size',
            'Max. presynaptic particle size',
            'Min. postsynaptic particle size',
            'Max. postsynaptic particle size']:
            label = QLabel(str1)
            grid3.addWidget(label, row, 0, alignment=Qt.AlignRight)
            row += 1

        # second column: data
        self.cb_imgType = QComboBox()
        self.cb_imgType.addItems(['Multi-channel', 'RGB'])
        self.cb_imgType.setCurrentIndex(0)      # Multi-channel
        self.cb_imgType.currentTextChanged.connect(self.img_type_changed)

        list1 = ['C1', 'C2', 'C3', 'C4', 'C5']
        self.cb_preChannelTag = QComboBox()
        self.cb_preChannelTag.addItems(list1)
        self.cb_preChannelTag.setCurrentIndex(0)    # C1
        self.cb_posChannelTag = QComboBox()
        self.cb_posChannelTag.addItems(list1)
        self.cb_posChannelTag.setCurrentIndex(2)    # C3

        list1 = ['Default', 'Huang', 'Intermodes', 'IsoData', 'IJ_IsoData', \
            'Li', 'MaxEntropy', 'Mean', 'MinError', 'Minimum', 'Moments', \
            'Otsu', 'Percentile', 'RenyiEntropy', 'Shanbhag', 'Triangle', 'Yen']
        self.cb_threshMethod = QComboBox()
        self.cb_threshMethod.addItems(list1)
        self.cb_threshMethod.setCurrentIndex(11)      # Otsu

        self.le_resizeWidth = QLineEdit('0')
        self.le_rollBallRad = QLineEdit('10.0')
        self.le_maxFiltRad  = QLineEdit('2.0')
        self.le_minSizePre  = QLineEdit('10.0')
        self.le_maxSizePre  = QLineEdit('400.0')
        self.le_minSizePos  = QLineEdit('10.0')
        self.le_maxSizePos  = QLineEdit('400.0')

        # place the widgets within the 3rd grid
        grid3.addWidget(self.cb_imgType,       1, 1)
        grid3.addWidget(self.cb_preChannelTag, 2, 1)
        grid3.addWidget(self.cb_posChannelTag, 3, 1)
        grid3.addWidget(self.le_resizeWidth,   4, 1)
        grid3.addWidget(self.le_rollBallRad,   5, 1)
        grid3.addWidget(self.le_maxFiltRad,    6, 1)
        grid3.addWidget(self.cb_threshMethod,  7, 1)
        grid3.addWidget(self.le_minSizePre,    8, 1)
        grid3.addWidget(self.le_maxSizePre,    9, 1)
        grid3.addWidget(self.le_minSizePos,   10, 1)
        grid3.addWidget(self.le_maxSizePos,   11, 1)

        # third column: units
        grid3.addWidget(QLabel('px'), 4, 2)
        for row in range(8, 12):
            grid3.addWidget(QLabel('px² or voxels'), row, 2)

        # some buttons
        pb_resetButton = QPushButton('Reset to defaults')
        pb_resetButton.setToolTip('Reset all fields to default values')
        pb_resetButton.clicked.connect(self.reset_button)
        pb_ok = QPushButton('OK')
        pb_ok.clicked.connect(self.ok_button)
        pb_cancel = QPushButton('Cancel')
        pb_cancel.clicked.connect(self.cancel_button)
        pb_help = QPushButton('Help')

        # place the widgets within the 4th grid
        grid4.addWidget(pb_resetButton, 0, 0)
        grid4.addWidget(pb_ok,          1, 1)
        grid4.addWidget(pb_cancel,      1, 2)
        grid4.addWidget(pb_help,        1, 3)

        # mount the whole stuff
        widget1.setLayout(vbox1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget1)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)


    def current_image(self):
        self.pb_inputButton.setEnabled(False)


    def batch_mode(self):
        self.pb_inputButton.setEnabled(True)


    def input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Input folder')
        self.lb_inputDirField.setText(folder)


    def save_intermediate_files(self):
        if self.xb_doOutputButton.isChecked():
            self.pb_outputButton.setEnabled(True)
        else:
            self.pb_outputButton.setEnabled(False)


    def output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Output folder')
        self.lb_outputDirField.setText(folder)


    def img_type_changed(self, img_type):
        if img_type == 'Multi-channel':
            list1 = ['C1', 'C2', 'C3', 'C4', 'C5']
        else:
            list1 = ['red', 'green', 'blue']

        # set new items in two combo-boxes
        self.cb_preChannelTag.clear()                # remove all items
        self.cb_preChannelTag.addItems(list1)
        self.cb_preChannelTag.setCurrentIndex(0)
        self.cb_posChannelTag.clear()
        self.cb_posChannelTag.addItems(list1)
        self.cb_posChannelTag.setCurrentIndex(1)


    def reset_button(self):
        self.rb_doOpenedImageButton.setChecked(True)
        self.rb_is2dButton.setChecked(True)
        self.pb_inputButton.setEnabled(False)
        self.lb_inputDirField.clear()
        self.xb_doSubFoldersButton.setChecked(False)
        self.xb_doOutputButton.setChecked(False)
        self.pb_outputButton.setEnabled(False)
        self.lb_outputDirField.clear()
        self.cb_imgType.setCurrentIndex(0)  # Multi-channel
        self.cb_preChannelTag.setCurrentIndex(0)  # red
        self.cb_posChannelTag.setCurrentIndex(2) # green
        self.le_resizeWidth.setText('0')
        self.le_rollBallRad.setText('10.0')
        self.le_maxFiltRad.setText('2.0')
        self.cb_threshMethod.setCurrentIndex(11) # Otsu
        self.le_minSizePre.setText('10.0')
        self.le_maxSizePre.setText('400.0')
        self.le_minSizePos.setText('10.0')
        self.le_maxSizePos.setText('400.0')


    def ok_button(self):
        parameter = self.get_parameter()
        print('parameter:', parameter)


    def cancel_button(self):
        self.close()


    def get_parameter(self):
        parameter = {
            'doOpenedImage': self.rb_doOpenedImageButton.isChecked(),
            'is3d':          self.rb_is3dButton.isChecked(),
            'doSubFolders':  self.xb_doSubFoldersButton.isChecked(),
            'doOutput':      self.xb_doOutputButton.isChecked(),
            'inputDir':      self.lb_inputDirField.text(),
            'outputDir':     self.lb_outputDirField.text(),
            'imgType':       self.cb_imgType.currentText(),
            'preChannelTag': self.cb_preChannelTag.currentText(),
            'posChannelTag': self.cb_posChannelTag.currentText(),
            'threshMethod':  self.cb_threshMethod.currentText(),
        }


        try:
            parameter['resizeWidth'] = int(self.le_resizeWidth.text())
        except ValueError as err:
            text = 'Integer value expected for resize image width:\n' + str(err)
            self.error_message(text)

        try:
            parameter['rollBallRad'] = float(self.le_rollBallRad.text())
        except ValueError as err:
            text = 'Float value expected for rolling ball radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['maxFiltRad'] = float(self.le_maxFiltRad.text())
        except ValueError as err:
            text = 'Float value expected for maximum filter radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['minSizePre'] = float(self.le_minSizePre.text())
        except ValueError as err:
            text = 'Integer value expected for presynaptic particle size:\n' + \
                str(err)
            self.error_message(text)

        try:
            parameter['maxSizePre'] = float(self.le_maxSizePre.text())
        except ValueError as err:
            text = 'Integer value expected for max. presynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['minSizePos'] = float(self.le_minSizePos.text())
        except ValueError as err:
            text = 'Integer value expected for min. postsynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['maxSizePos'] = float(self.le_maxSizePos.text())
        except ValueError as err:
            text = 'Integer value expected for max. postsynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)
        return parameter


    def error_message(self, text):
        err_box = QMessageBox(self)
        err_box.setWindowTitle('Error!')
        err_box.setText(text)
        button = err_box.exec()
        if button == QMessageBox.Ok:
            pass


    def __str__(self):
        formatstr = 'Analyze synaptics:\n' + \
            '\tChoose input source: current image=%s, batch mode=%s\n' + \
            '\tInput dimensionality: 2D=%s, 3D=%s\n' + \
            '\tInput Folder: %s\n' + \
            '\tSearch in subfolders: %s\n' + \
            '\tSave intermediate files: %s\n' + \
            '\tOutput folder: %s\n' + \
            '\tImage type: %s\n' + \
            '\tPresynaptic protein channel: %s\n' + \
            '\tPostsynaptic protein channel: %s\n' + \
            '\tResize image width: %s px\n' + \
            '\tRolling ball radius: %s\n' + \
            '\tMaximum filter radius: %s\n' + \
            '\tMethod for threshold adjustment: %s\n' + \
            '\tPresynaptic particle size: %s px² or voxels\n' + \
            '\tMax. presynaptic particle size: %s px² or voxels\n' + \
            '\tMin. postsynaptic particle size: %s px² or voxels\n' + \
            '\tMax. postsynaptic particle size: %s px² or voxels\n'
        data = (str(self.rb_doOpenedImageButton.isChecked()),
                str(self.rb_doBatchButton.isChecked()),
                str(self.rb_is2dButton.isChecked()),
                str(self.rb_is3dButton.isChecked()),
                self.lb_inputDirField.text(),
                str(self.xb_doSubFoldersButton.isChecked()),
                str(self.xb_doOutputButton.isChecked()),
                self.lb_outputDirField.text(),
                self.cb_imgType.currentText(),
                self.cb_preChannelTag.currentText(),
                self.cb_posChannelTag.currentText(),
                self.le_resizeWidth.text(),
                self.le_rollBallRad.text(),
                self.le_maxFiltRad.text(),
                self.cb_threshMethod.currentText(),
                self.le_minSizePre.text(),
                self.le_maxSizePre.text(),
                self.le_minSizePos.text(),
                self.le_maxSizePos.text())
        return formatstr % data
