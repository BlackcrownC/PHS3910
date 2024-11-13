import numpy as np
import scipy.integrate as integrate
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from scipy.special import jn
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from PIL import Image
import matplotlib.cm as cm

poisson_mean = 20000

D = 1 #(um^2/s)

number_of_photons = np.random.poisson(poisson_mean,size=1)
photon_list = np.arange(0,number_of_photons,1) + 1
emission_time = np.sort(np.random.uniform(0,1,number_of_photons))
time_between_emissions = np.diff(emission_time) 

sigma = np.sqrt(2*D*time_between_emissions)
mu = 0
pos = np.linspace(-1,1,1000) #(um)
dx = np.zeros(len(sigma))
dy = np.zeros(len(sigma))
for i in range(len(sigma)):
    dx[i] = np.random.normal(0,sigma[i])
    dy[i] = np.random.normal(0,sigma[i])
x_diff = np.cumsum(dx)
y_diff = np.cumsum(dy)
t = np.array(np.cumsum(time_between_emissions))

sigma_photons = 0.1 # (um)
x_psf = x_diff+np.random.normal(loc=0,scale=sigma_photons,size=len(x_diff))
y_psf = y_diff+np.random.normal(0,sigma_photons,len(y_diff))

num_frames = 50
time_groups = 0.1*np.linspace(0,10,num_frames+1)
binsize = 0.1 # (um)
x_range = (x_psf.min(), x_psf.max())
y_range = (y_psf.min(), y_psf.max())
num_bins_x = int((x_range[1] - x_range[0]) / binsize)
num_bins_y = int((y_range[1] - y_range[0]) / binsize)

def gaussian_2d(xy, amp, x0, y0, sigma_x, sigma_y):
    x, y = xy
    return amp * np.exp(-(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2)))
  

def gaussian_fit(zdata,xdata,ydata):
    x, y = np.meshgrid(xdata, ydata)
    # Flatten the data for curve_fit
    xfit = x.ravel()
    yfit = y.ravel()
    zfit = zdata.ravel()
    # Estimate initial x0 and y0 based on the peak
    peak_index = np.unravel_index(np.argmax(zdata), zdata.shape)
    x0_guess = xdata[peak_index[1]]  # Corresponding x value
    y0_guess = ydata[peak_index[0]]  # Corresponding y value
    params_guess = (100,x0_guess,y0_guess,0.4,0.4)
    lower_bounds = [10, min(xdata), min(ydata), 0.1, 0.01]
    upper_bounds = [200, max(xdata), max(ydata), 1, 1]
    # Fit the data
    popt, pcov = curve_fit(gaussian_2d, (xfit,yfit), zfit, p0=params_guess, bounds=(lower_bounds, upper_bounds), maxfev=10000)
    return popt

x_loc = np.zeros(len(time_groups)-1)
y_loc = np.zeros(len(time_groups)-1)
av_x = np.zeros(len(time_groups)-1)
av_y = np.zeros(len(time_groups)-1)

images = []
for i in range(len(time_groups)-1):
    index = np.where((time_groups[i] <= t)&(t < time_groups[i+1]))[0]
    hist, xedges, yedges = np.histogram2d(x_psf[index], y_psf[index], bins=(num_bins_x, num_bins_y),
                                          range=[x_range, y_range])
    av_x[i] = np.mean(x_diff[index])
    av_y[i] = np.mean(y_diff[index])
    x_centers = (xedges[:-1] + xedges[1:]) / 2
    y_centers = (yedges[:-1] + yedges[1:]) / 2
    params = gaussian_fit(hist.T,x_centers, y_centers)
    x_loc[i] = params[1]
    y_loc[i] = params[2]

    plt.figure()
    plt.imshow(hist.T, extent=(x_range[0], x_range[1], y_range[0], y_range[1]), origin='lower', cmap='viridis')
    plt.colorbar(label='Photon Count')
    plt.plot(params[1], params[2], 'ro', label='Gaussian Center')
    plt.title(f'Frame {i + 1}')
    plt.xlabel('X Position (um)')
    plt.ylabel('Y Position (um)')
    plt.legend()

    # Save the plot as an image
    plt.savefig(f'frame_{i + 1}.png')
    images.append(Image.open(f'frame_{i + 1}.png'))
    plt.close()

# Save images as multipage TIFF
images[0].save('particle_movement_gaussian_fit.tiff', save_all=True, append_images=images[1:], format='TIFF')
print("Multipage TIFF file saved as 'particle_movement_gaussian_fit.tiff'")

plt.figure(figsize=(8, 8))
norm = plt.Normalize(time_groups.min(), time_groups.max())
colors = cm.viridis(norm(time_groups))  # Color according to time

for i in range(len(x_loc) - 1):
    plt.plot(x_loc[i:i+2], y_loc[i:i+2], color=colors[i])

plt.xlabel("X Position (μm)")
plt.ylabel("Y Position (μm)")
plt.title(f"Trajectory of Emitter in X-Y Plane (D = {D} μm²/s)")
plt.colorbar(cm.ScalarMappable(norm=norm, cmap='viridis'), label="Time (s)")
plt.grid()
plt.show()
