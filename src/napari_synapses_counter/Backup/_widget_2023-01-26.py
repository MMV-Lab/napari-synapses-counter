import numpy as np
from napari.layers import Image
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
from tifffile import imread, imwrite


class SynapsesCounter(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # arange the layouts
        grid1 = QGridLayout()
        grid2 = QGridLayout()
        grid3 = QGridLayout()
        grid4 = QGridLayout()

        vbox1 = QVBoxLayout()
        vbox1.addLayout(grid1)
        vbox1.addLayout(grid2)
        vbox1.addLayout(grid3)
        vbox1.addLayout(grid4)

        widget1 = QWidget()
        widget1.setLayout(vbox1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget1)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)

        # Choose input source
        grid1.addWidget(QLabel('Choose input source:'), 0, 0)
        self.rb_currentImage = QRadioButton('current image')
        self.rb_currentImage.setChecked(True)
        self.rb_currentImage.clicked.connect(self.input_source)
        grid1.addWidget(self.rb_currentImage, 0, 1)

        self.rb_batchMode = QRadioButton('batch mode')
        self.rb_batchMode.clicked.connect(self.input_source)
        grid1.addWidget(self.rb_batchMode, 0, 2)

        bg1 = QButtonGroup(widget1)
        bg1.addButton(self.rb_currentImage)
        bg1.addButton(self.rb_batchMode)

        # Input dimensionality
        grid1.addWidget(QLabel('Input dimensionality:'), 1, 0)
        self.rb_2D = QRadioButton('2D')
        self.rb_2D.setChecked(True)
        grid1.addWidget(self.rb_2D, 1, 1)

        self.rb_3D = QRadioButton('3D')
        grid1.addWidget(self.rb_3D, 1, 2)

        bg2 = QButtonGroup(widget1)
        bg2.addButton(self.rb_2D)
        bg2.addButton(self.rb_3D)

        # Input Folder
        self.b_inputFolder = QPushButton('Input folder')
        self.b_inputFolder.clicked.connect(self.input_folder)
        self.b_inputFolder.setEnabled(False)
        grid2.addWidget(self.b_inputFolder, 0, 0)

        self.l_inputFolder = QLabel()
        grid2.addWidget(self.l_inputFolder, 0, 1)

        # Search in subfolders
        self.xb_searchInSubfolders = QCheckBox('search in subfolders')
        self.xb_searchInSubfolders.setChecked(False)
        grid2.addWidget(self.xb_searchInSubfolders, 1, 0)

        # Save intermediate files
        self.xb_saveIntermediate = QCheckBox('save intermediate files')
        self.xb_saveIntermediate.setChecked(False)
        self.xb_saveIntermediate.clicked.connect(self.save_intermediate_files)
        grid2.addWidget(self.xb_saveIntermediate, 2, 0)

        # Output folder
        self.b_outputFolder = QPushButton('Output folder')
        self.b_outputFolder.clicked.connect(self.output_folder)
        self.b_outputFolder.setEnabled(False)
        grid2.addWidget(self.b_outputFolder, 3, 0)

        self.l_outputFolder = QLabel()
        grid2.addWidget(self.l_outputFolder, 3, 1)

        # Select image
        self.b_selectImage = QPushButton('Select image')
        self.b_selectImage.clicked.connect(self.select_image)
        grid2.addWidget(self.b_selectImage, 4, 0)

        self.cb_selectImage = QComboBox()
        grid2.addWidget(self.cb_selectImage, 4, 1)

        # Analysis settings
        label = QLabel('Analysis settings:')
        grid3.addWidget(label, 0, 0, alignment=Qt.AlignCenter)

        # first column: label
        row = 1
        for lbl in [
            'Image type:',
            'Presynaptic protein channel:',
            'Postsynaptic protein channel:',
            'Resize image width:',
            'Rolling ball radius:',
            'Maximum filter radius:',
            'Method of threshold adjustment:',
            'Min. distance for peak_local_max',
            'Presynaptic particle size',
            'Max. presynaptic particle size',
            'Min. postsynaptic particle size',
            'Max. postsynaptic particle size',
            'Lower overlap limit']:
            label = QLabel(lbl)
            grid3.addWidget(label, row, 0, alignment=Qt.AlignRight)
            row += 1

        # second column: data
        # Image type
        self.cb_imageType = QComboBox()
        self.cb_imageType.addItems(['Multi-channel', 'RGB'])
        self.cb_imageType.setCurrentIndex(1)      # RGB
        self.cb_imageType.currentTextChanged.connect(self.image_type)
        grid3.addWidget(self.cb_imageType, 1, 1)

        # Presynaptic protein channel
        self.cb_preChannel = QComboBox()
        self.cb_preChannel.addItems(['red', 'green', 'blue'])
        self.cb_preChannel.setCurrentIndex(0)    # red
        grid3.addWidget(self.cb_preChannel,  2, 1)

        # Postsynaptic protein channel
        self.cb_postChannel = QComboBox()
        self.cb_postChannel.addItems(['red', 'green', 'blue'])
        self.cb_postChannel.setCurrentIndex(1)   # green
        grid3.addWidget(self.cb_postChannel, 3, 1)

        # Resize image width
        self.le_resizeImageWidth = QLineEdit('0')
        grid3.addWidget(self.le_resizeImageWidth, 4, 1)
        grid3.addWidget(QLabel('px'), 4, 2)

        # Rolling ball radius
        self.le_rollingBallRadius = QLineEdit('10.0')
        grid3.addWidget(self.le_rollingBallRadius, 5, 1)

        # Maximum Filter Radius
        self.le_maxFilterRadius = QLineEdit('2.0')
        grid3.addWidget(self.le_maxFilterRadius, 6, 1)

        # Method of threshold adjustment
        list1 = ['Isodata', 'Li', 'Mean', 'Minimum', 'Otsu', 'Triangle', 'Yen']
        self.cb_threshMethod = QComboBox()
        self.cb_threshMethod.addItems(list1)
        self.cb_threshMethod.setCurrentIndex(4)     # Otsu
        grid3.addWidget(self.cb_threshMethod, 7, 1)

        # Minimum distance for peak_local_max()
        self.le_minDistance = QLineEdit('15')
        grid3.addWidget(self.le_minDistance, 8, 1)
        grid3.addWidget(QLabel('px'), 8, 2)

        # Min and max presynaptic particle size
        self.le_minSizePre = QLineEdit('10.0')
        grid3.addWidget(self.le_minSizePre, 9, 1)

        self.le_maxSizePre = QLineEdit('400.0')
        grid3.addWidget(self.le_maxSizePre, 10, 1)

        # Min and max postsynaptic particle size
        self.le_minSizePost = QLineEdit('10.0')
        grid3.addWidget(self.le_minSizePost, 11, 1)

        self.le_maxSizePost = QLineEdit('400.0')
        grid3.addWidget(self.le_maxSizePost, 12, 1)

        # Lower overlap limit
        self.le_overlapLimit = QLineEdit('10.0')
        grid3.addWidget(self.le_overlapLimit, 13, 1)
        grid3.addWidget(QLabel('%'), 13, 2)

        # third column: units
        for row in range(9, 13):
            grid3.addWidget(QLabel('px² or voxels'), row, 2)

        # some buttons
        b_reset = QPushButton('Reset to defaults')
        b_reset.setToolTip('Reset all fields to default values')
        b_reset.clicked.connect(self.reset)
        grid4.addWidget(b_reset, 0, 0)

        b_OK = QPushButton('OK')
        b_OK.clicked.connect(self.ok_button)
        grid4.addWidget(b_OK, 0, 1)

        b_cancel = QPushButton('Cancel')
        b_cancel.clicked.connect(self.cancel)
        grid4.addWidget(b_cancel, 0, 2)

        # b_help = QPushButton('Help')
        # grid4.addWidget(b_help, 0, 3)


    def input_source(self):
        rb = self.sender()
        if rb.text() == 'current image':
            self.b_inputFolder.setEnabled(False)
        else:
            self.b_inputFolder.setEnabled(True)


    def input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Input folder')
        self.l_inputFolder.setText(folder)


    def save_intermediate_files(self):
        if self.xb_saveIntermediate.isChecked():
            self.b_outputFolder.setEnabled(True)
        else:
            self.b_outputFolder.setEnabled(False)


    def output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Output folder')
        self.l_outputFolder.setText(folder)


    def select_image(self):
        self.cb_selectImage.clear()
        for layer in self.viewer.layers:
            self.cb_selectImage.addItem(layer.name)


    def image_type(self, img_type):
        if img_type == 'Multi-channel':
            list1 = ['C1', 'C2', 'C3', 'C4', 'C5']
        else:
            list1 = ['red', 'green', 'blue']

        # set new items in two combo-boxes
        self.cb_preChannel.clear()                # remove all items
        self.cb_preChannel.addItems(list1)
        self.cb_preChannel.setCurrentIndex(0)
        self.cb_postChannel.clear()
        self.cb_postChannel.addItems(list1)
        self.cb_postChannel.setCurrentIndex(1)


    def reset(self):
        self.rb_currentImage.setChecked(True)
        self.rb_2D.setChecked(True)
        self.b_inputFolder.setEnabled(False)
        self.l_inputFolder.clear()
        self.xb_searchInSubfolders.setChecked(False)
        self.xb_saveIntermediate.setChecked(False)
        self.b_outputFolder.setEnabled(False)
        self.l_outputFolder.clear()
        self.cb_selectImage.clear()
        self.cb_imageType.setCurrentIndex(0)        # Multi-channel
        self.cb_preChannel.setCurrentIndex(0)       # C1
        self.cb_postChannel.setCurrentIndex(2)      # C3
        self.le_resizeImageWidth.setText('0')
        self.le_rollingBallRadius.setText('10.0')
        self.le_maxFilterRadius.setText('2.0')
        self.cb_threshMethod.setCurrentIndex(4)     # Otsu
        self.le_minDistance.setText('15')
        self.le_minSizePre.setText('10.0')
        self.le_maxSizePre.setText('400.0')
        self.le_minSizePost.setText('10.0')
        self.le_maxSizePost.setText('400.0')
        self.le_overlapLimit.setText('10.0')


    def ok_button(self):
        parameter = self.get_parameter()
        # print('parameter:', parameter)    # test output
        if parameter['Error'] == True:
            return
        self.runSynapseCounter(parameter)


    def cancel(self):
        self.close()


    def get_parameter(self):
        parameter = {
            'currentImage':         self.rb_currentImage.isChecked(),
            'batchMode':            self.rb_batchMode.isChecked(),
            'is2D':                 self.rb_2D.isChecked(),
            'is3D':                 self.rb_3D.isChecked(),
            'searchInSubfolders':   self.xb_searchInSubfolders.isChecked(),
            'saveIntermediate':     self.xb_saveIntermediate.isChecked(),
            'inputFolder':          self.l_inputFolder.text(),
            'outputFolder':         self.l_outputFolder.text(),
            'imageType':            self.cb_imageType.currentText(),
            'preChannelTag':        self.cb_preChannel.currentText(),
            'postChannelTag':       self.cb_postChannel.currentText(),
            'threshMethod':         self.cb_threshMethod.currentText(),
            'Error':                False,
        }


        try:
            parameter['resizeImageWidth'] = int(self.le_resizeImageWidth.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Integer value expected for resize image width:\n' + str(err)
            self.error_message(text)

        try:
            parameter['rollingBallRadius'] = \
                float(self.le_rollingBallRadius.text())
        except ValueError as err:
            parameter['Error'] = True
            text = 'Float value expected for rolling ball radius:\n' + str(err)
            self.error_message(text)

        try:
            parameter['maxFilterRadius'] = float(self.le_maxFilterRadius.text())
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
        errorBox = QMessageBox(self)
        errorBox.setWindowTitle('Error!')
        errorBox.setText(text)
        button = errorBox.exec()
        if button == QMessageBox.Ok:
            pass


    def runSynapseCounter(self, parameter):
        for layer in self.viewer.layers:
            #if layer.name == 'control11' and type(layer) == Image:
            if type(layer) == Image:
                image = layer.data
                break

        if parameter['imageType'] == 'Multi-channel':
            if parameter['preChannelTag'] == 'C1':
                preChannel = image[0, :, :]
            elif parameter['preChannelTag'] == 'C2':
                preChannel = image[1, :, :]
            elif parameter['preChannelTag'] == 'C3':
                preChannel = image[2, :, :]
            elif parameter['preChannelTag'] == 'C4':
                preChannel = image[3, :, :]
            elif parameter['preChannelTag'] == 'C5':
                preChannel = image[4, :, :]

            if parameter['postChannelTag'] == 'C1':
                postChannel = image[0, :, :]
            elif parameter['postChannelTag'] == 'C2':
                postChannel = image[1, :, :]
            elif parameter['postChannelTag'] == 'C3':
                postChannel = image[2, :, :]
            elif parameter['postChannelTag'] == 'C4':
                postChannel = image[3, :, :]
            elif parameter['postChannelTag'] == 'C5':
                postChannel = image[4, :, :]

        elif parameter['imageType'] == 'RGB':
            if parameter['preChannelTag'] == 'red':
                preChannel = image[:, :, 0]
            elif parameter['preChannelTag'] == 'green':
                preChannel = image[:, :, 1]
            elif parameter['preChannelTag'] == 'blue':
                preChannel = image[:, :, 2]

            if parameter['postChannelTag'] == 'red':
                postChannel = image[:, :, 0]
            elif parameter['postChannelTag'] == 'green':
                postChannel = image[:, :, 1]
            elif parameter['postChannelTag'] == 'blue':
                postChannel = image[:, :, 2]

        # Evaluate the presynaptic protein channel
        preChannel = self.cleanUp(preChannel, parameter)
        self.viewer.add_image(data=preChannel, name='presynaptic proteins')

        # Evaluate the postsynaptic protein channel
        postChannel = self.cleanUp(postChannel, parameter)
        self.viewer.add_image(data=postChannel, name='postsynaptic proteins')

        # Determine an overlap mask (single class) and calculate a region
        # segmentation with watershed
        overlapMask = self.calculate_overlap(preChannel, postChannel, \
            parameter['overlapLimit'])
        overlapMask = self.region_segmentation(overlapMask, parameter)
        self.viewer.add_image(data=overlapMask, name='overlap mask')

        properties = regionprops_table(overlapMask, properties=('label', \
            'centroid', 'equivalent_diameter_area'))
        label = properties['label']
        centroid0 = properties['centroid-0']
        centroid1 = properties['centroid-1']
        diameter = properties['equivalent_diameter_area']
        meanDiameter = np.mean(diameter)
        print('mean(diameter)', meanDiameter, 'px')

        """points = np.concatenate((centroid0, centroid1))
        print('type(points)', type(points))
        print('shape', points.shape)
        print('dtype', points.dtype) """


    def cleanUp(self, channel, parameter):
        # Step 1: skimage.transform.resize
        rows, cols = channel.shape
        if (parameter['resizeImageWidth'] > 0) and \
            (parameter['resizeImageWidth'] != cols):
            factor = parameter['resizeImageWidth'] / cols
            resizeHeight = rows * factor
            resizeHeight = int(round(resizeHeight, 0))
            channel = resize(channel, (resizeHeight, \
                parameter['resizeImageWidth']))

        # Step 2: scipy.ndimage.gaussian_filter
        channel = gaussian_filter(channel, sigma=2)

        # Step 3: skimage.restoration.rolling_ball and background subtraction
        background = rolling_ball(channel, radius=parameter['rollingBallRadius'])
        channel = channel - background

        # Step 4: skimage.morphology.remove_small_objects
        channel = remove_small_objects(channel, parameter['maxFilterRadius'])

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


    def region_segmentation(self, overlapMask, parameter):
        # a) Calculate the Euclidean distance to the background
        distance = distance_transform_edt(overlapMask)

        # b) Find the local maxima of 'distance'
        coords = peak_local_max(distance, min_distance=parameter['minDistance'], \
            labels=overlapMask)
        mask = np.zeros(distance.shape, dtype=bool)
        mask[tuple(coords.T)] = True

        # c) label features in the array 'mask'
        markers, num_features = label(mask)

        # d) Find watershed basins in 'distance' flooded from given markers
        result = watershed(-distance, markers, mask=overlapMask)
        print('num_features', num_features)
        return result


    def calculate_overlap(self, preChannel, postChannel, overlapLimit):
        # Preset the mask with zeros
        overlap_mask = np.zeros(preChannel.shape, dtype=int)
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
