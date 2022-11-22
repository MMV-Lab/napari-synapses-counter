import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, \
    QPushButton, QRadioButton, QCheckBox, QLineEdit, QComboBox, \
    QVBoxLayout, QGridLayout, QButtonGroup, QScrollArea, QFileDialog, \
    QMessageBox
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget()

        # Definition of the required layouts
        vbox1 = QVBoxLayout()
        grid1 = QGridLayout()
        grid2 = QGridLayout()
        grid3 = QGridLayout()
        grid4 = QGridLayout()

        # Arange the layouts
        vbox1.addLayout(grid1)
        vbox1.addLayout(grid2)
        vbox1.addLayout(grid3)
        vbox1.addLayout(grid4)

        # Two labels in the first column
        row = 0
        for str1 in [
            'Choose input source:',
            'Input dimensionality:']:
            label = QLabel(str1)
            grid1.addWidget(label, row, 0)
            row += 1

        # Input_source
        self.rb_cur_img = QRadioButton('current image')
        self.rb_cur_img.setChecked(True)
        self.rb_cur_img.clicked.connect(self.current_image)
        self.rb_batch_md = QRadioButton('batch mode')
        self.rb_batch_md.clicked.connect(self.batch_mode)

        btn_grp1 = QButtonGroup(self.widget)
        btn_grp1.addButton(self.rb_cur_img)
        btn_grp1.addButton(self.rb_batch_md)

        # Input dimensionality
        self.rb_2d = QRadioButton('2D')
        self.rb_2d.setChecked(True)
        self.rb_3d = QRadioButton('3D')

        btn_grp2 = QButtonGroup(self.widget)
        btn_grp2.addButton(self.rb_2d)
        btn_grp2.addButton(self.rb_3d)

        # Place the widgets within the grid
        grid1.addWidget(self.rb_cur_img,  0, 1)
        grid1.addWidget(self.rb_batch_md, 0, 2)
        grid1.addWidget(self.rb_2d,       1, 1)
        grid1.addWidget(self.rb_3d,       1, 2)

        # Input and output files
        self.pb_inp_fldr = QPushButton('Input folder')
        self.pb_inp_fldr.clicked.connect(self.input_folder)
        self.pb_inp_fldr.setEnabled(False)
        self.lb_inp_fldr = QLabel()

        self.xb_sub_fldr = QCheckBox('search in subfolders')
        self.xb_sub_fldr.setChecked(False)
        self.xb_svim_file = QCheckBox('save intermediate files')
        self.xb_svim_file.setChecked(False)
        self.xb_svim_file.clicked.connect(self.save_intermediate_files)

        self.pb_outp_fldr = QPushButton('OutputFolder')
        self.pb_outp_fldr.clicked.connect(self.output_folder)
        self.pb_outp_fldr.setEnabled(False)
        self.lb_outp_fldr = QLabel()

        # Place the widgets within the grid
        grid2.addWidget(self.pb_inp_fldr,  0, 0)
        grid2.addWidget(self.lb_inp_fldr,  0, 1)
        grid2.addWidget(self.xb_sub_fldr,  1, 0)
        grid2.addWidget(self.xb_svim_file, 2, 0)
        grid2.addWidget(self.pb_outp_fldr, 3, 0)
        grid2.addWidget(self.lb_outp_fldr, 3, 1)

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
        self.cb_img_type = QComboBox()
        self.cb_img_type.addItems(['Multi-channel', 'RGB'])
        self.cb_img_type.setCurrentIndex(0)      # Multi-channel
        self.cb_img_type.currentTextChanged.connect(self.img_type_changed)

        list1 = ['C1', 'C2', 'C3', 'C4', 'C5']
        self.cb_pre_prot = QComboBox()
        self.cb_pre_prot.addItems(list1)
        self.cb_pre_prot.setCurrentIndex(0)      # C1
        self.cb_post_prot = QComboBox()
        self.cb_post_prot.addItems(list1)
        self.cb_post_prot.setCurrentIndex(2)     # C3

        self.le_img_width = QLineEdit('0')
        self.le_ball_rad = QLineEdit('10.0')
        self.le_max_flt_rad = QLineEdit('2.0')

        list1 = ['Default', 'Huang', 'Intermodes', 'IsoData', 'IJ_IsoData', \
            'Li', 'MaxEntropy', 'Mean', 'MinError', 'Minimum', 'Moments', \
            'Otsu', 'Percentile', 'RenyiEntropy', 'Shanbhag', 'Triangle', 'Yen']
        self.cb_thr_adj = QComboBox()
        self.cb_thr_adj.addItems(list1)
        self.cb_thr_adj.setCurrentIndex(11)      # Otsu

        #5th Min. and max. particle size
        self.le_pre_ps = QLineEdit('10')
        self.le_max_pre_ps = QLineEdit('400')
        self.le_min_post_ps = QLineEdit('10')
        self.le_max_post_ps = QLineEdit('400')

        grid3.addWidget(self.cb_img_type,     1, 1)
        grid3.addWidget(self.cb_pre_prot,     2, 1)
        grid3.addWidget(self.cb_post_prot,    3, 1)
        grid3.addWidget(self.le_img_width,    4, 1)
        grid3.addWidget(self.le_ball_rad,     5, 1)
        grid3.addWidget(self.le_max_flt_rad,  6, 1)
        grid3.addWidget(self.cb_thr_adj,      7, 1)
        grid3.addWidget(self.le_pre_ps,       8, 1)
        grid3.addWidget(self.le_max_pre_ps,   9, 1)
        grid3.addWidget(self.le_min_post_ps, 10, 1)
        grid3.addWidget(self.le_max_post_ps, 11, 1)

        #third column: units
        label = QLabel('px')
        grid3.addWidget(label, 4, 2)
        for row in range(8, 12):
            label = QLabel('px² or voxels')
            grid3.addWidget(label, row, 2)

        # Some buttons
        pb_reset = QPushButton('Reset to defaults')
        pb_reset.setToolTip('Reset all fields to default values')
        pb_reset.clicked.connect(self.reset_button)
        pb_ok = QPushButton('OK')
        pb_ok.clicked.connect(self.ok_button)
        pb_cancel = QPushButton('Cancel')
        pb_cancel.clicked.connect(self.cancel_button)
        pb_help = QPushButton('Help')

        # Place the widgets within the grid
        grid4.addWidget(pb_reset,  0, 0)
        grid4.addWidget(pb_ok,     1, 1)
        grid4.addWidget(pb_cancel, 1, 2)
        grid4.addWidget(pb_help,   1, 3)

        # Mount the whole stuff
        self.widget.setLayout(vbox1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.widget)
        self.setCentralWidget(scroll)
        self.setWindowTitle("Analyze synapses")


    def current_image(self):
        # print('vars(self)', vars(self))
        self.pb_inp_fldr.setEnabled(False)


    def batch_mode(self):
        self.pb_inp_fldr.setEnabled(True)


    def input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Input folder')
        self.lb_inp_fldr.setText(folder)


    def save_intermediate_files(self):
        if self.xb_svim_file.isChecked():
            self.pb_outp_fldr.setEnabled(True)
        else:
            self.pb_outp_fldr.setEnabled(False)


    def output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Output folder')
        self.lb_outp_fldr.setText(folder)


    def img_type_changed(self, img_type):
        if img_type == 'Multi-channel':
            list1 = ['C1', 'C2', 'C3', 'C4', 'C5']
        else:
            list1 = ['red', 'green', 'blue']

        # set new items in two combo-boxes
        self.cb_pre_prot.clear()                # remove all items
        self.cb_pre_prot.addItems(list1)
        self.cb_pre_prot.setCurrentIndex(0)
        self.cb_post_prot.clear()
        self.cb_post_prot.addItems(list1)
        self.cb_post_prot.setCurrentIndex(1)


    def reset_button(self):
        self.rb_cur_img.setChecked(True)
        self.rb_2d.setChecked(True)
        self.pb_inp_fldr.setEnabled(False)
        self.lb_inp_fldr.clear()
        self.xb_sub_fldr.setChecked(False)
        self.xb_svim_file.setChecked(False)
        self.pb_outp_fldr.setEnabled(False)
        self.lb_outp_fldr.clear()
        self.cb_img_type.setCurrentIndex(0)  # Multi-channel
        self.cb_pre_prot.setCurrentIndex(0)  # red
        self.cb_post_prot.setCurrentIndex(2) # green
        self.le_img_width.setText('0')
        self.le_ball_rad.setText('10.0')
        self.le_max_flt_rad.setText('2.0')
        self.cb_thr_adj.setCurrentIndex(11) # Otsu
        self.le_pre_ps.setText('10')
        self.le_max_pre_ps.setText('400')
        self.le_min_post_ps.setText('10')
        self.le_max_post_ps.setText('400')


    def ok_button(self):
        parameter = self.get_parameter()
        print('parameter:', parameter)


    def cancel_button(self):
        self.close()


    def get_parameter(self):
        parameter = {
            'input_source': 'current image' if self.rb_cur_img.isChecked()
                else 'batch mode',
            'input_dimensionality': '2D' if self.rb_2d.isChecked()
                else '3D',
            'input_folder':                   self.lb_inp_fldr.text(),
            'search_in_subfolders':           str(self.xb_sub_fldr.isChecked()),
            'save_intermediate_files':        str(self.xb_svim_file.isChecked()),
            'output_folder':                  self.lb_outp_fldr.text(),
            'image_type':                     self.cb_img_type.currentText(),
            'presynaptic_protein_channel':    self.cb_pre_prot.currentText(),
            'postsynaptic_protein_channel':   self.cb_post_prot.currentText(),
            'method_of_threshold_adjustment': self.cb_thr_adj.currentText(),
        }

        try:
            parameter['resize_image_width'] = int(self.le_img_width.text())
        except ValueError as err:
            text = 'Integer value expected for resize image width:\n' + str(err)
            self.error_message(text)

        try:
            parameter['rolling_ball_radius'] = float(self.le_ball_rad.text())
        except ValueError as err:
            text = 'Float value expected for rolling ball radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['maximum_filter_radius'] = float(self.le_max_flt_rad.text())
        except ValueError as err:
            text = 'Float value expected for maximum filter radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['presynaptic_particle_size'] = int(self.le_pre_ps.text())
        except ValueError as err:
            text = 'Integer value expected for presynaptic particle size:\n' + \
                str(err)
            self.error_message(text)

        try:
            parameter['max_presynaptic_particle_size'] = \
                int(self.le_max_pre_ps.text())
        except ValueError as err:
            text = 'Integer value expected for max. presynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['min_postsynaptic_particle_size'] = \
                int(self.le_min_post_ps.text())
        except ValueError as err:
            text = 'Integer value expected for min. postsynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['max_postsynaptic_particle_size'] = \
                int(self.le_max_post_ps.text())
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
        data = (str(self.rb_cur_img.isChecked()),
                str(self.rb_batch_md.isChecked()),
                str(self.rb_2d.isChecked()),
                str(self.rb_3d.isChecked()),
                self.lb_inp_fldr.text(),
                str(self.xb_sub_fldr.isChecked()),
                str(self.xb_svim_file.isChecked()),
                self.lb_outp_fldr.text(),
                self.cb_img_type.currentText(),
                self.cb_pre_prot.currentText(),
                self.cb_post_prot.currentText(),
                self.le_img_width.text(),
                self.le_ball_rad.text(),
                self.le_max_flt_rad.text(),
                self.cb_thr_adj.currentText(),
                self.le_pre_ps.text(),
                self.le_max_pre_ps.text(),
                self.le_min_post_ps.text(),
                self.le_max_post_ps.text())
        return formatstr % data


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
