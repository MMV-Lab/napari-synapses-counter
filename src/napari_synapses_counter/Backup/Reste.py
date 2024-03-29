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


    def read_image(self, parameter)
        (fname, filter) = QFileDialog.getOpenFileName(self,
            'Select an image file', 'c:\\', 'Tiff files (*.tiff *.tif)')

        if fname == '':     # User pressed 'Cancel'
            return
        else:
            image = imread(fname)
            print('fname', fname)
            #print('type(image)', type(image))
            print('image.shape', image.shape)
            print('image.ndim', image.ndim)
            #print('image.size', image.size)
            print('image.dtype', image.dtype)


    def runSynapseCounter(self, parameter):
        minSize = min(parameter['minSizePre'], parameter['minSizePost'])
        maxSize = max(parameter['maxSizePre'], parameter['maxSizePost'])

        if parameter['is3d']:
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
                minSize, maxSize, 0.0, 1.0))



