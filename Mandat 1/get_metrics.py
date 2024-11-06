import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.io import loadmat

# Functions to calculate the resolution and contrast

def load_from_mat(file_path):
    # load the correlation matrix from a .mat file
    mat = loadmat(file_path)
    return mat['corr_mat_3D']

def gaussian_2d(xy, amplitude, x0, y0, sigma_x, sigma_y, C):
    # define a 2D gaussian function
    x, y = xy
    f = amplitude * np.exp(-((x-x0)**2 / (2*sigma_x**2) + (y-y0)**2 / (2*sigma_y**2))) + C
    return f.ravel()

def get_metrics(data):
    # calculate the contrast
    maximum = np.max(data)
    threshold = 0.3*maximum
    noise = data[data < threshold]
    baseline = np.mean(noise)
    contrast = maximum - baseline

    # taking only a 16x16 region of interest around the maximum
    y_position, x_position = np.unravel_index(np.argmax(data), data.shape)
    data = data[y_position-8:y_position+8, x_position-8:x_position+8]

    # create a meshgrid
    x = np.linspace(0, data.shape[1], data.shape[1])
    y = np.linspace(0, data.shape[0], data.shape[0])
    x, y = np.meshgrid(x, y)
    
    # fit the data to a 2D gaussian
    lower_bounds = (0, 0, 0, 0, 0, 0)
    upper_bounds = (1, x.max(), y.max(), np.inf, np.inf, np.inf)
    popt, _ = curve_fit(gaussian_2d, (x, y), data.ravel(), p0=[np.max(data), 8, 8, 1.5, 1.5, baseline],  bounds=(lower_bounds, upper_bounds)) 

    # get the average FWHM
    fwhm_x = 2 * np.sqrt(2 * np.log(2)) * popt[3]
    fwhm_y = 2 * np.sqrt(2 * np.log(2)) * popt[4]
    fwhm = (fwhm_x + fwhm_y) / 2
    
    # conversion factor from pixels to mm
    hauteur = 0.62 # m
    nb_pixel_hauteur = data.shape[0]
    factor = hauteur/nb_pixel_hauteur*1000
    resolution = fwhm*factor

    return resolution, contrast
