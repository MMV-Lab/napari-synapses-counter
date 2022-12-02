import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt, label
from skimage.feature import peak_local_max
from skimage.filters import threshold_isodata, threshold_li, threshold_mean, \
    threshold_minimum, threshold_otsu, threshold_triangle, threshold_yen
from skimage.morphology import remove_small_objects
from skimage.restoration import rolling_ball
from skimage.segmentation import watershed
from skimage.transform import resize
from tifffile import imread, imwrite
from tkinter.filedialog import askopenfilename


def cleanUp(channel, parameter):
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
    print('channel.shape', channel.shape)
    print('channel.ndim', channel.ndim)
    print('channel.dtype', channel.dtype)

    plt.imshow(channel)
    #imwrite('result.tif', channel)


def runCleanUp(fname):
    if fname == '':     # User pressed 'Cancel'
        print('Good-by')
        return
    else:
        image = imread(fname)
        print('fname', fname)
        # print('type(image)', type(image))
        print('image.shape', image.shape)
        print('image.ndim', image.ndim)
        # print('image.size', image.size)
        print('image.dtype', image.dtype)

    preChannel = image[:, :, 0]
    posChannel = image[:, :, 1]
    parameter = {
        'resizeWidth':  1024,
        'rollBallRad':  10.0,
        'maxFiltRad':   1.0,
        'threshMethod': 'Otsu',
        'minDistance':  15,
    }
    cleanUp(preChannel, parameter)


fname = askopenfilename(initialdir='.', title='Select file')
runCleanUp(fname)
plt.show()