import matplotlib.pyplot as plt
from napari.layers import Image
import numpy as np
from pandas import DataFrame
from qtpy.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, \
    QPushButton, QRadioButton, QCheckBox, QLineEdit, QComboBox, \
    QVBoxLayout, QGridLayout, QButtonGroup, QScrollArea, QFileDialog, \
    QMessageBox
from qtpy.QtCore import Qt
from scipy.ndimage import gaussian_filter, distance_transform_edt, label
from skimage.feature import peak_local_max
from skimage.filters import threshold_isodata, threshold_li, threshold_mean, \
    threshold_minimum, threshold_otsu, threshold_triangle, threshold_yen
from skimage.measure import regionprops_table
from skimage.morphology import remove_small_objects
from skimage.restoration import rolling_ball
from skimage.segmentation import watershed
from skimage.transform import resize
import sys
from tifffile import imread, imwrite


class MyParticleAnalyzer:
    def __init__(self, minSize, maxSize, minCirc, maxCirc):
        self.myCount = 0
        self.myTotalSize = 0
        self.mySumSqSize = 0
        print('call ParticleAnalyzer,', 'minSize', minSize, 'maxSize', maxSize)


class MyParticleAnalyzer3D:
    def __init__(self, minSize, maxSize, minCirc, maxCirc):
        self.myCount = 0
        self.myTotalSize = 0
        self.mySumSqSize = 0
        self.minSize = int(round(minSize, 0))
        self.maxSize = int(round(maxSize, 0))
        print('do whatever it has to do,', 'minSize', minSize, 'maxSize', maxSize)


class SynapsesCounter(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.partAnalyzers = []
        self.partAnalyzers3D = []

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
            'Minimum distance for local max',
            'Presynaptic particle size',
            'Max. presynaptic particle size',
            'Min. postsynaptic particle size',
            'Max. postsynaptic particle size',
            'Overlap lower limit']:
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
        self.cb_postChannelTag = QComboBox()
        self.cb_postChannelTag.addItems(list1)
        self.cb_postChannelTag.setCurrentIndex(2)   # C3

        list1 = ['Default', 'Huang', 'Intermodes', 'IsoData', 'IJ_IsoData', \
            'Li', 'MaxEntropy', 'Mean', 'MinError', 'Minimum', 'Moments', \
            'Otsu', 'Percentile', 'RenyiEntropy', 'Shanbhag', 'Triangle', 'Yen']
        self.cb_threshMethod = QComboBox()
        self.cb_threshMethod.addItems(list1)
        self.cb_threshMethod.setCurrentIndex(11)      # Otsu

        self.le_resizeWidth  = QLineEdit('0')
        self.le_rollBallRad  = QLineEdit('10.0')
        self.le_maxFiltRad   = QLineEdit('2.0')
        self.le_minDistance  = QLineEdit('15')
        self.le_minSizePre   = QLineEdit('10.0')
        self.le_maxSizePre   = QLineEdit('400.0')
        self.le_minSizePost  = QLineEdit('10.0')
        self.le_maxSizePost  = QLineEdit('400.0')
        self.le_overlapLimit = QLineEdit('10.0')

        # place the widgets within the 3rd grid
        grid3.addWidget(self.cb_imgType,        1, 1)
        grid3.addWidget(self.cb_preChannelTag,  2, 1)
        grid3.addWidget(self.cb_postChannelTag, 3, 1)
        grid3.addWidget(self.le_resizeWidth,    4, 1)
        grid3.addWidget(self.le_rollBallRad,    5, 1)
        grid3.addWidget(self.le_maxFiltRad,     6, 1)
        grid3.addWidget(self.cb_threshMethod,   7, 1)
        grid3.addWidget(self.le_minDistance,    8, 1)
        grid3.addWidget(self.le_minSizePre,     9, 1)
        grid3.addWidget(self.le_maxSizePre,    10, 1)
        grid3.addWidget(self.le_minSizePost,   11, 1)
        grid3.addWidget(self.le_maxSizePost,   12, 1)
        grid3.addWidget(self.le_overlapLimit,  13, 1)

        # third column: units
        grid3.addWidget(QLabel('px'), 4, 2)
        grid3.addWidget(QLabel('px'), 8, 2)
        grid3.addWidget(QLabel('%'), 13, 2)
        for row in range(9, 13):
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
        self.cb_postChannelTag.clear()
        self.cb_postChannelTag.addItems(list1)
        self.cb_postChannelTag.setCurrentIndex(1)


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
        self.cb_postChannelTag.setCurrentIndex(2) # green
        self.le_resizeWidth.setText('0')
        self.le_rollBallRad.setText('10.0')
        self.le_maxFiltRad.setText('2.0')
        self.cb_threshMethod.setCurrentIndex(11) # Otsu
        self.lw_minDistance.setText('15')
        self.le_minSizePre.setText('10.0')
        self.le_maxSizePre.setText('400.0')
        self.le_minSizePost.setText('10.0')
        self.le_maxSizePost.setText('400.0')
        self.le_overlapLimit.setText('10.0')


    def ok_button(self):
        parameter = self.get_parameter()
        print('parameter:', parameter)    # test output
        if parameter['Error'] == True:
            return
        self.runSynapseCounter(parameter)


    def cancel_button(self):
        self.close()


    def get_parameter(self):
        parameter = {
            'doOpenedImage':    self.rb_doOpenedImageButton.isChecked(),
            'is3d':             self.rb_is3dButton.isChecked(),
            'doSubFolders':     self.xb_doSubFoldersButton.isChecked(),
            'doOutput':         self.xb_doOutputButton.isChecked(),
            'inputDir':         self.lb_inputDirField.text(),
            'outputDir':        self.lb_outputDirField.text(),
            'imgType':          self.cb_imgType.currentText(),
            'preChannelTag':    self.cb_preChannelTag.currentText(),
            'postChannelTag':   self.cb_postChannelTag.currentText(),
            'threshMethod':     self.cb_threshMethod.currentText(),
            'Error':            False,
        }


        try:
            parameter['resizeWidth'] = int(self.le_resizeWidth.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Integer value expected for resize image width:\n' + str(err)
            self.error_message(text)

        try:
            parameter['rollBallRad'] = float(self.le_rollBallRad.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for rolling ball radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['maxFiltRad'] = float(self.le_maxFiltRad.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for maximum filter radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['minDistance'] = int(self.le_minDistance.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Integer value expected for minimum distance:\n' + str(err)
            self.error_message(text)

        try:
            parameter['minSizePre'] = float(self.le_minSizePre.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for presynaptic particle size:\n' + \
                str(err)
            self.error_message(text)

        try:
            parameter['maxSizePre'] = float(self.le_maxSizePre.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for max. presynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['minSizePost'] = float(self.le_minSizePost.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for min. postsynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['maxSizePost'] = float(self.le_maxSizePost.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for max. postsynaptic particle ' + \
                'size:\n' + str(err)
            self.error_message(text)

        try:
            parameter['overlapLimit'] = float(self.le_overlapLimit.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for overlap lower limit:\n' + str(err)
            self.error_message(text)
        return parameter


    def error_message(self, text):
        err_box = QMessageBox(self)
        err_box.setWindowTitle('Error!')
        err_box.setText(text)
        button = err_box.exec()
        if button == QMessageBox.Ok:
            pass


    def runSynapseCounter(self, parameter):
        minSize = min(parameter['minSizePre'], parameter['minSizePost'])
        maxSize = max(parameter['maxSizePre'], parameter['maxSizePost'])

        '''if parameter['is3d']:
            self.partAnalyzers3D.append(MyParticleAnalyzer3D( \
                parameter['minSizePre'], parameter['maxSizePre'], 0.0, 1.0))
            self.partAnalyzers3D.append(MyParticleAnalyzer3D( \
                parameter['minSizePost'], parameter['maxSizePost'], 0.0, 1.0))
            self.partAnalyzers3D.append(MyParticleAnalyzer3D( \
                minSize, maxSize, 0.0, 1.0))
        else:
            self.partAnalyzers.append(MyParticleAnalyzer( \
                parameter['minSizePre'], parameter['maxSizePre'], 0.0, 1.0))
            self.partAnalyzers.append(MyParticleAnalyzer( \
                parameter['minSizePost'], parameter['maxSizePost'], 0.0, 1.0))
            self.partAnalyzers.append(MyParticleAnalyzer( \
                minSize, maxSize, 0.0, 1.0)) '''

        for layer in self.viewer.layers:
            #if layer.name == 'control11' and type(layer) == Image:
            if type(layer) == Image:
                image = layer.data
                break

        if parameter['imgType'] == 'Multi-channel':
            print('Not jet implemented!')
            return
        elif parameter['imgType'] == 'RGB':
            if parameter['preChannelTag']   == 'red':
                preChannel = image[:, :, 0]
            elif parameter['preChannelTag'] == 'green':
                preChannel = image[:, :, 1]
            elif parameter['preChannelTag'] == 'blue':
                preChannel = image[:, :, 2]

            if parameter['postChannelTag']   == 'red':
                postChannel = image[:, :, 0]
            elif parameter['postChannelTag'] == 'green':
                postChannel = image[:, :, 1]
            elif parameter['postChannelTag'] == 'blue':
                postChannel = image[:, :, 2]

        # Work with the presynaptic protein channel
        preChannel = self.cleanUp(preChannel, parameter)
        self.viewer.add_image(data=preChannel, name='presynaptic proteins')

        preProps = regionprops_table(preChannel, properties=('label', 'centroid', \
            'equivalent_diameter_area', 'eccentricity'))
        df = DataFrame(preProps)
        #print(df)

        # Work with the postsynaptic protein channel
        postChannel = self.cleanUp(postChannel, parameter)
        self.viewer.add_image(data=postChannel, name='postsynaptic proteins')

        postProps = regionprops_table(postChannel, properties=('label', 'centroid', \
            'equivalent_diameter_area', 'eccentricity'))
        df = DataFrame(postProps)
        #print(df)

        #overlapMask = np.logical_and(preChannel, postChannel)
        overlapMask = self.calculate_overlap(preChannel, postChannel, \
            parameter['overlapLimit'])
        self.viewer.add_image(data=overlapMask, name='overlap mask')


    def cleanUp(self, channel, parameter):
        # Step 1: skimage.transform.resize
        rows, cols = channel.shape
        if (parameter['resizeWidth'] > 0) and (parameter['resizeWidth'] != cols):
            factor = parameter['resizeWidth'] / cols
            resizeHeight = rows * factor
            resizeHeight = int(round(resizeHeight, 0))
            channel = resize(channel, (resizeHeight, parameter['resizeWidth']))

        # Step 2: scipy.ndimage.gaussian_filter
        channel = gaussian_filter(channel, sigma=2)

        # Step 3: skimage.restoration.rolling_ball and background subtraction
        background = rolling_ball(channel, radius=parameter['rollBallRad'])
        channel = channel - background

        # Step 4: skimage.morphology.remove_small_objects
        channel = remove_small_objects(channel, parameter['maxFiltRad'])

        # Step 5: skimage.filters.threshold_xxx
        if parameter['threshMethod'] == 'Isodata':
            threshold = threshold_isodata(channel)
        elif parameter['threshMethod'] == 'Li':
            threshold = threshold_li(channel)
        elif parameter['threshMethod'] == 'Mean':
            threshold = threshold_mean(channel)
        elif parameter['threshMethod'] == 'Minimum':
            threshold = threshold_minimum(channel)
        elif parameter['threshMethod'] == 'Otsu':
            threshold = threshold_otsu(channel)
        elif parameter['threshMethod'] == 'Triangle':
            threshold = threshold_triangle(channel)
        elif parameter['threshMethod'] == 'Yen':
            threshold = threshold_yen(channel)
        channel = channel > threshold

        # Step 6: skimage.segmentation.watershed
        # a) Calculate the Euclidean distance to the background
        distance = distance_transform_edt(channel)

        # b) Find the local maxima of 'distance'
        coords = peak_local_max(distance, min_distance=parameter['minDistance'], \
            labels=channel)
        mask = np.zeros(distance.shape, dtype=bool)
        mask[tuple(coords.T)] = True

        # c) label features in the array 'mask'
        markers, num_features = label(mask)

        # d) Find watershed basins in 'distance' flooded from given markers
        channel = watershed(-distance, markers, mask=channel)
        print('num_features', num_features)
        return channel


    def calculate_overlap(self, preChannel, postChannel, overlapLimit):
        # Preset the mask with zeros
        overlap_mask = np.zeros(preChannel.shape)
        overlapLimit /= 100.0           # overlapLimit is in %

        # find the numbers of segments in the preChannel
        preSegments = np.unique(preChannel)
        # The segment with the number 0 is the background
        if preSegments[0] == 0:
            preSegments = preSegments[1:]

        # loop over all preSegments
        for seg_i in preSegments:
            # coordinates of the pixels in preSegment seg_i
            r1, c1 = np.where(preChannel == seg_i)
            sizePreSegment = len(r1)

            # find all postSegments within preSegment seg_i
            postSegments = np.unique(postChannel[r1, c1])
            # The segment with the number 0 is the background
            if postSegments[0] == 0:
                postSegments = postSegments[1:]
            if len(postSegments) == 0:      # no overlap found
                continue

            # loop over the found postSegments
            for seg_j in postSegments:
                # coordinates of the pixels in postSegment seg_j
                r2, c2 = np.where(postChannel == seg_j)
                sizePostSegment = len(r2)

                minSizeSegment = min(sizePreSegment, sizePostSegment)
                minOverlap = int(minSizeSegment * overlapLimit)

                # coordinates of the overlapped pixels
                r3, c3 = np.where((preChannel == seg_i) & (postChannel == seg_j))
                sizeOverlap = len(r3)
                if sizeOverlap < minOverlap:
                    continue
                else:
                    # mark the found pixels
                    overlap_mask[r3, c3] = 1

        return overlap_mask
