import numpy as np
from scipy.special import jn
import scipy.integrate as integrate
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from scipy.special import jn
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from PIL import Image
import matplotlib.cm as cm
import io

poisson_mean = 20000

kb = 1.38e-23 # J/K
r = 1e-6 # m
T = 20 + 273 # K
n = 1.0016e-3
D = (((kb*T)/(6*np.pi*n*r))*1e12)
number_of_photons = np.random.poisson(poisson_mean,size=1)
photon_list = np.arange(0,number_of_photons,1) + 1
emission_time = np.sort(np.random.uniform(0,1,number_of_photons))
time_between_emissions = np.diff(emission_time)

sigma = np.sqrt(2*D*time_between_emissions)
mu = 0
dx = np.zeros(len(sigma))
dy = np.zeros(len(sigma))
for i in range(len(sigma)):
    dx[i] = np.random.normal(0,sigma[i])
    dy[i] = np.random.normal(0,sigma[i])
x_diff = np.cumsum(dx)
y_diff = np.cumsum(dy)
print(x_diff)
t = np.array(np.cumsum(time_between_emissions))

sigma_photons = 0.1 # (um)
x_psf = x_diff+np.random.normal(loc=0,scale=sigma_photons,size=len(x_diff))
y_psf = y_diff+np.random.normal(0,sigma_photons,len(y_diff))

num_frames = 10
time_groups = 0.1*np.linspace(0,10,num_frames+1)

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

    x0_guess = xdata[peak_index[0]]  # Corresponding x value
    y0_guess = ydata[peak_index[1]]  # Corresponding y value
    params_guess = (zdata.max(),x0_guess,y0_guess,0.4,0.4)
    lower_bounds = [0, min(xdata), min(ydata), 0.1, 0.01]
    upper_bounds = [1000, max(xdata), max(ydata), 1, 1]
    # Fit the data
    popt, pcov = curve_fit(gaussian_2d, (xfit,yfit), zfit, p0=params_guess, bounds=(lower_bounds, upper_bounds), maxfev=10000)
    return popt

x_loc = np.zeros(len(time_groups)-1)
y_loc = np.zeros(len(time_groups)-1)
av_x = np.zeros(len(time_groups)-1)
av_y = np.zeros(len(time_groups)-1)

images = []
l_tube = 150 #mm
l_obj = 5 #mm
M = l_tube/l_obj  # Microscope magnification
effective_pixel_size = 3.45 / M  # Effective pixel size in um
camera_width = 1440
camera_height = 1080
x_psf_scaled = (x_psf / effective_pixel_size)+(1440//2)
y_psf_scaled = (y_psf / effective_pixel_size)+(1080//2)

x_range_2 = (x_psf_scaled.min(), x_psf_scaled.max())  # Adjusted field of view for X
y_range_2 = (y_psf_scaled.min(), y_psf_scaled.max())   # Adjusted field of view for Y

# Adjusted loop for generating frames
for i in range(len(time_groups) - 1):
    index = np.where((time_groups[i] <= t) & (t < time_groups[i + 1]))[0]
    hist, xedges, yedges = np.histogram2d(
        x_psf_scaled[index], y_psf_scaled[index], bins=(int(1440/M), int(1080/M)), 
        range = [((camera_width//2-int(camera_width/M)),(camera_width//2+int(camera_height/M)) ),
                (camera_height//2-int(camera_height/M),(camera_height//2+ int(camera_height/M)))]
    )

    av_x[i] = np.mean(x_diff[index]) 
    av_y[i] = np.mean(y_diff[index])
    x_centers = (xedges[:-1] + xedges[1:]) / 2
    y_centers = (yedges[:-1] + yedges[1:]) / 2

    # Gaussian fitting and localization
    params = gaussian_fit(hist.T, x_centers, y_centers)
    x_loc[i] = params[1]
    y_loc[i] = params[2]

    # Visualization of the current frame
    plt.figure()
    plt.imshow(hist.T, extent=(0,1440,0,1080), origin='lower', cmap='viridis')
    plt.colorbar(label='Photon Count')
    plt.plot(params[1], params[2], 'ro', label='Gaussian Center')
    plt.title(f'Frame {i + 1}')
    plt.xlabel('X Position (um)')
    plt.ylabel('Y Position (um)')
    plt.legend()

    # Save the plot as an image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    images.append(buf)
    plt.close()
    print(i)

time_center = (time_groups[:-1] + time_groups[1:]) / 2
# Save images as a multipage TIFF
images = [Image.open(buf) for buf in images]
images[0].save('particle_movement_gaussian_fit.tiff', save_all=True, append_images=images[1:], format='TIFF')
print("Multipage TIFF file saved as 'particle_movement_gaussian_fit.tiff'")

plt.figure(figsize=(8, 8))
norm = plt.Normalize(time_center.min(), time_center.max())
colors = cm.viridis(norm(time_center))  # Color according to time

for i in range(len(x_loc) - 1):
    plt.plot(x_loc[i:i+2], y_loc[i:i+2], color=colors[i])

plt.xlabel("X Position (μm)")
plt.ylabel("Y Position (μm)")
plt.title(f"Trajectory of Emitter in X-Y Plane (D = {D} μm²/s)")
plt.colorbar(cm.ScalarMappable(norm=norm, cmap='viridis'), label="Time (s)")
plt.grid()
plt.show()

time_lags = np.array([1,2,3,4,5])
av_sdx = np.zeros(len(time_lags))
av_sdy = np.zeros(len(time_lags))
av_sd = np.zeros(len(time_lags))

for i, tau in enumerate(time_lags):
    sdx = []
    sdy = []
    sd = []
    
    # Loop over each starting point in the data array for the given lag
    for j in range(len(x_loc) - tau):
        dx = x_loc[j + tau] - x_loc[j]
        dy = y_loc[j + tau] - y_loc[j]
        sdx.append(dx ** 2)
        sdy.append(dy ** 2)
        sd.append(dx**2 + dy**2)
        
    av_sdx[i] = np.mean(sdx)
    av_sdy[i] = np.mean(sdy)
    av_sd[i] = np.mean(sd)

real_time_lags = (time_center[1]-time_center[0])*time_lags

def line(x,m,b):
    return m*np.array(x) + b

popt, pcov = curve_fit(line,real_time_lags,av_sd)
fitted_line = line(real_time_lags,*popt)

plt.scatter(time_lags, av_sd, label='Average squared displacements x and y',color='g')
plt.plot(time_lags,fitted_line, label='Fitted linear model',color='orange')
plt.scatter(time_lags, av_sdx, label='Average sdx', color='b')
plt.scatter(time_lags, av_sdy, label='Average sdy', color='r')
plt.xlabel('Time lags')
plt.ylabel('Average squared displacement (um^2)')
plt.legend()
plt.grid(True)
plt.show()
#rint(f"Fitted values : m = {round(popt[0],4)}, b = {round(popt[1],4)}.")

kb = 1.38e-23 # J/K
r = np.linspace(1e-6,10e-6,1000) # m
T = 20 + 273 # K
n = 1.0016 # Viscosity of water at 20
D2 = (kb*T)/(6*np.pi*n*r)

plt.figure(figsize=(8, 6))
plt.plot(r, D2, label='$D_2 = \\frac{k_B T}{6 \\pi \\eta r}$', color='b')
plt.xlabel('Radius $r$ (m)')
plt.ylabel('Diffusion Coefficient $D_2$ (m$^2$/s)')
plt.title('Diffusion Coefficient $D_2$ vs. Radius $r$')
plt.grid(True)
plt.legend()
#plt.show()