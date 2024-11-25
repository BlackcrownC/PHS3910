import numpy as np
from scipy.special import jn
import scipy.integrate as integrate
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from PIL import Image
import matplotlib.cm as cm
import io

poisson_mean = 2000000

kb = 1.38e-23 # J/K
r = 1e-6 # m
T = 20 + 273 # K
n = 1.0016e-3
D = (((kb*T)/(6*np.pi*n*r))*1e12)
print(D)
NA = 1.5
l = 405e-9
# var_r = np.array([1e-6, 5e-6, 10e-6])  # Radii in meters
# var_m = np.linspace(50, 500, 10)  # Magnifications
# errors = np.zeros((len(var_r), len(var_m)))
def psf(r) : 
    return (2*jn(1,(2*np.pi*NA*r)/(l))/((2*np.pi*NA*r)/(l)))**2

r_image = np.linspace(-5e-6,5e-6,1000)
#plt.plot(r_image, psf(r_image), label="PSF")

def gaussian(x, A, mu, sigma):
    return A * np.exp(- (x - mu)**2 / (2 * sigma**2))

number_of_photons = np.random.poisson(poisson_mean,size=1)

psf_val = psf(r_image)
psf_val /= integrate.trapezoid(psf_val, r_image) 
cdf = np.cumsum(psf_val) * np.diff(r_image, prepend=r_image[0])
inverse_cdf = interpolate.interp1d(cdf, r_image, bounds_error=False, fill_value=(r_image[0], r_image[-1]))
u = np.random.uniform(0,1,number_of_photons)  
photon_positions_r = inverse_cdf(u)  
photon_positions_x = photon_positions_r * np.cos(2 * np.pi * np.random.uniform(0,1,number_of_photons)) 
binwidth = 1e-6 
bins = np.arange(-5e-6, 5e-6 + binwidth, binwidth)
photon_positions_x_microns = photon_positions_x * 1e6 
counts, bin_edges = np.histogram(photon_positions_x_microns, bins=bins * 1e6)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2 
initial_guess = [np.max(counts), 0, 1] 
params__, covariance = curve_fit(gaussian, bin_centers, counts, p0=initial_guess)
A_fit, mu_fit, sigma_fit = params__
x_fit = np.linspace(min(bin_centers), max(bin_centers), 1000)
y_fit = gaussian(x_fit, A_fit, mu_fit, sigma_fit)
#plt.plot(x_fit, y_fit, color='red', label='Gaussian')
print(sigma_fit)
# initial_guess = [1,0,1e-6]
# params, covariance = curve_fit(gaussian, r_image, psf(r_image), p0=initial_guess)

# A_fit, mu_fit, sigma_fit = params
# gaussian_fit = gaussian(r_image, *params)
# print(sigma_fit)
# plt.plot(r_image, gaussian_fit, label = 'curve fit')

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

sigma_photons = sigma_fit # (um)
x_psf = x_diff+np.random.normal(loc=0,scale=sigma_photons,size=len(x_diff))
y_psf = y_diff+np.random.normal(0,sigma_photons,len(y_diff))

num_frames = 50
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

    # print("zdata", zdata.min(), zdata.max())
    # print("xdata range:", xdata.min(), xdata.max())
    # print("ydata range:", ydata.min(), ydata.max())

    x0_guess = xdata[peak_index[1]]  # Corresponding x value
    y0_guess = ydata[peak_index[0]]  # Corresponding y value
    params_guess = (zdata.max(),x0_guess,y0_guess, 3, 3)
    print(params_guess)
    lower_bounds = [0, min(xdata), min(ydata), 1, 1]
    upper_bounds = [1000, max(xdata), max(ydata), 10, 10]
    # Fit the data
    popt, pcov = curve_fit(gaussian_2d, (xfit,yfit), zfit, p0=params_guess, bounds=(lower_bounds, upper_bounds), maxfev=10000)
    return popt

x_loc = np.zeros(len(time_groups)-1)
y_loc = np.zeros(len(time_groups)-1)
x_loc_2 = np.zeros(len(time_groups)-1)
y_loc_2 = np.zeros(len(time_groups)-1)
av_x = np.zeros(len(time_groups)-1)
av_y = np.zeros(len(time_groups)-1)

images = []
M = 1000 # Microscope magnification
effective_pixel_size = 3.45 / M  # Effective pixel size in um
camera_width = 1440
camera_height = 1080
x_psf_scaled = (x_psf / effective_pixel_size)+(1440//2)
y_psf_scaled = (y_psf / effective_pixel_size)+(1080//2)

# Adjusted loop for generating frames
for i in range(1) :
    index = np.where((time_groups[i] <= t) & (t < time_groups[i + 1]))[0]
    hist, xedges, yedges = np.histogram2d(
        x_psf_scaled[index], y_psf_scaled[index], bins=(int(1440), int(1080)),
        range = [(0,camera_width), (0,camera_height)]
    )
    av_x[i] = np.mean(x_diff[index])
    av_y[i] = np.mean(y_diff[index])    
    x_centers = (xedges[:-1] + xedges[1:]) / 2
    y_centers = (yedges[:-1] + yedges[1:]) / 2
    # Gaussian fitting and localization
    params = gaussian_fit(hist.T, x_centers, y_centers)
    x_loc[i] = params[1]
    y_loc[i] = params[2]
    x_loc_2[i], y_loc_2[i] = (params[1]-(camera_width // 2))*effective_pixel_size, (params[2]-camera_height//2)*effective_pixel_size
    print(x_loc[i], x_loc_2[i])
    # Visualization of the current frame
    plt.figure()
    plt.imshow(hist.T, extent=(0,1440,0,1080) , origin='lower', cmap='viridis', norm=None, vmin=0, vmax=hist.max())
    plt.xlim(600,800)
    plt.ylim(450,650)
    plt.colorbar(label='Photon Count')
    plt.scatter(params[1], params[2], color='red', label=f'Centre : {int(params[1])} , {int(params[2])}', s=2, zorder=5)
    #print([params[1], params[2]])
    #plt.title(f'Position localisée : {int(params[1])}, {int(params[2])}')
    plt.xlabel('X Position (pixel)')
    plt.ylabel('Y Position (pixel)')
    plt.legend()

    # Save the plot as an image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    images.append(buf)
    # img=Image.open(buf)
    plt.close()
    # if i == 0:
    #     first_frame = img
    # if i == 4:  # Replace 4 with `num_frames-1` for the last frame
    #     last_frame = img
    # if i == 9 :
    #     last_last_frame = img
    print(i)
    print(f"Total photons in histogram: {hist.sum()} (Expected: {number_of_photons})")
    print(f"Histogram max count: {hist.max()}")
time_center = (time_groups[:-1] + time_groups[1:]) / 2
# if first_frame:
#     first_frame.save('first_frame.png', format='PNG')
#     print("First frame saved as 'first_frame.tiff'")
# if last_frame:
#     last_frame.save('second_frame.png', format='PNG')
#     print("Second frame saved as 'last_frame.tiff'")
# if last_last_frame:
#     last_last_frame.save('last_frame.png', format='PNG')
#     print("Last frame saved as 'last_frame.tiff'")
# Save images as a multipage TIFF
images = [Image.open(buf) for buf in images]
images[0].save('particle_movement_gaussian_fit.tiff', save_all=True, append_images=images[1:], format='TIFF')
print("Multipage TIFF file saved as 'particle_movement_gaussian_fit.tiff'")
images[0].save(
    'trajectory_animation.gif', save_all=True, append_images=images[1:],
    duration=100, loop=0  # Duration in ms (adjust for speed), loop=0 for infinite looping
)

## Figure deplacement selon x et y
plt.figure(figsize=(8, 8))
norm = plt.Normalize(time_center.min(), time_center.max())
colors = cm.viridis(norm(time_center))  # Color according to time

for i in range(len(x_loc) - 1):
    plt.plot(x_loc[i:i+2], y_loc[i:i+2], color=colors[i])

plt.xlabel("X Position (μm)")
plt.ylabel("Y Position (μm)")
plt.title(f"Trajectire de la particule (D = {D} μm²/s)")
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
        dx = x_loc_2[j + tau] - x_loc_2[j]
        dy = y_loc_2[j + tau] - y_loc_2[j]
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

plt.scatter(real_time_lags, av_sd, label='Déplacement quadratique moyen',color='g')
plt.plot(real_time_lags,fitted_line, label='Ajustement linéaire',color='orange')
#plt.scatter(real_time_lags, av_sdx, label='Average sdx', color='b')
#plt.scatter(real_time_lags, av_sdy, label='Average sdy', color='r')
plt.xlabel('Décalage temporel')
plt.ylabel('Déplacement quadratique moyen (um^2)')
plt.legend()
plt.grid(True)
plt.show()
print(f"Fitted values : m = {round(popt[0],4)}, b = {round(popt[1],4)}.")
D2 = (popt[0]/4)
print('D2 = ' , D2)
error_time_lags = np.abs(D2-D)/D
r_2 = (((kb*T)/(6*np.pi*n*D2))*1e12)
print(r_2)
