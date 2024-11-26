import numpy as np
from scipy.special import jn
import scipy.integrate as integrate
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from PIL import Image
import matplotlib.cm as cm
import io

# Constants
poisson_mean = 2000000
kb = 1.38e-23  # J/K
T = 293  # Temperature in K (20°C)
n = 1.0016e-3  # Viscosity of the medium
NA = 1.5  # Numerical Aperture
l = 405e-9  # Wavelength in meters
num_frames = 50
camera_width = 1440
camera_height = 1080
time_groups = 0.1 * np.linspace(0, 10, num_frames + 1)
binwidth = 1e-6

# Particle radius and magnifications
var_r = np.array([1e-6])  # Radius in meters
var_m = np.array([50])  # Magnification, minimum 50 (plus petit le gaussian_fit marche pas)
errors = np.zeros((len(var_r), len(var_m)))

# Point Spread Function
def psf(r):
    return (2 * jn(1, (2 * np.pi * NA * r) / l) / ((2 * np.pi * NA * r) / l)) ** 2

# Gaussian fitting functions
def gaussian_1d(x, A, mu, sigma):
    return A * np.exp(- (x - mu) ** 2 / (2 * sigma ** 2))

def gaussian_2d(xy, amp, x0, y0, sigma_x, sigma_y):
    x, y = xy
    return amp * np.exp(-(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2)))

def gaussian_fit(zdata, xdata, ydata):
    x, y = np.meshgrid(xdata, ydata)
    xfit, yfit, zfit = x.ravel(), y.ravel(), zdata.ravel()
    peak_index = np.unravel_index(np.argmax(zdata), zdata.shape)
    params_guess = (zdata.max(), xdata[peak_index[1]], ydata[peak_index[0]], 3, 3)
    bounds = ([0, min(xdata), min(ydata), 1, 1], [1000, max(xdata), max(ydata), 20, 20])
    popt, _ = curve_fit(gaussian_2d, (xfit, yfit), zfit, p0=params_guess, bounds=bounds, maxfev=10000)
    return popt

def line(x,m,b):
    return m*np.array(x) + b
    
number_of_photons = np.random.poisson(poisson_mean,size=1)

# Section pour trouver le sigma de la PSF
r_image = np.linspace(-5e-6,5e-6,1000)
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
params, covariance = curve_fit(gaussian_1d, bin_centers, counts, p0=initial_guess)
A_fit, mu_fit, sigma_fit = params
x_fit = np.linspace(min(bin_centers), max(bin_centers), 1000)
y_fit = gaussian_1d(x_fit, A_fit, mu_fit, sigma_fit)

r_diff = [] # juste utile pour faire plusieurs zoom d'une shot

# Main simulation loop
for r_idx, r in enumerate(var_r):
    D = (kb * T / (6 * np.pi * n * r)) * 1e12  # Diffusion coefficient
    number_of_photons = np.random.poisson(poisson_mean)
    emission_time = np.sort(np.random.uniform(0, 1, number_of_photons))
    time_between_emissions = np.diff(emission_time)
    sigma_diffusion = np.sqrt(2 * D * time_between_emissions)
    t = np.array(np.cumsum(time_between_emissions))
    dx = np.random.normal(0, sigma_diffusion)
    dy = np.random.normal(0, sigma_diffusion)
    x_diff = np.cumsum(dx)
    y_diff = np.cumsum(dy)
    # print(y_diff)
    # print(D)
    for m_idx, M in enumerate(var_m):
        effective_pixel_size = 3.45 / M
        x_diff_scaled = (x_diff / effective_pixel_size) + (camera_width // 2)
        y_diff_scaled = (y_diff / effective_pixel_size) + (camera_height // 2)
        x_psf = x_diff+np.random.normal(loc=0,scale=sigma_fit,size=len(x_diff))
        y_psf = y_diff+np.random.normal(0,sigma_fit,len(y_diff))
        x_psf_scaled = (x_psf / effective_pixel_size) + (camera_width // 2)
        y_psf_scaled = (y_psf / effective_pixel_size) + (camera_height // 2)

        x_loc = np.zeros(len(time_groups) - 1)
        y_loc = np.zeros(len(time_groups) - 1)
        av_x = np.zeros(len(time_groups) - 1)
        av_y = np.zeros(len(time_groups) - 1)

        print(f'Grossissement : {M}')
        for frame in range(num_frames):
            idx = np.where((time_groups[frame] <= t) & (t < time_groups[frame + 1]))[0]
            av_x[frame] = np.mean(x_diff[idx])
            av_y[frame] = np.mean(y_diff[idx])
            
            hist, xedges, yedges = np.histogram2d(
                x_psf_scaled[idx], y_psf_scaled[idx],
                bins=(camera_width, camera_height),
                range=[(0, camera_width), (0, camera_height)]
            )

            x_centers = (xedges[:-1] + xedges[1:]) / 2
            y_centers = (yedges[:-1] + yedges[1:]) / 2
            params = gaussian_fit(hist.T, x_centers, y_centers)
            x_loc[frame], y_loc[frame] = (params[1]-(camera_width // 2))*effective_pixel_size, (params[2]-camera_height//2)*effective_pixel_size
            print(f'Frame {frame} en cours')
            #print(x_loc[frame], y_loc[frame])
            # plt.figure()
            # plt.imshow(hist.T, extent=(0,1440,0,1080), origin='lower', cmap='viridis')
            # plt.colorbar(label='Photon Count')
            # plt.scatter(params[1], params[2], color='red', label='Gaussian center', s=2, zorder=5)
            # # print([params[1], params[2]])
            # plt.title(f'Frame {frame + 1}')
            # plt.xlabel('X Position (um)')
            # plt.ylabel('Y Position (um)')
            # plt.legend()
            # plt.show()
        print(x_loc)
        time_center = (time_groups[:-1] + time_groups[1:]) / 2

        time_lags = np.array([1,2])
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

        popt, pcov = curve_fit(line,real_time_lags,av_sd)
        fitted_line = line(real_time_lags,*popt)
        D2 = popt[0]/4
        print(f'Le coefficient de diffusion retrouve est : {D2}')
        r = (((kb*T)/(6*np.pi*n*D2))*1e12)
        print(f'Le rayon trouve pour un zoom {M} est : {r}')
        r_diff.append(r)
        # Calculate error for current r and M

        # x_err = av_x - x_loc
        # y_err = av_y - y_loc
        # print(x_err)
        # print(y_err)
        # errors[r_idx, m_idx] = np.sqrt(x_err**2 + y_err**2).mean()

# print(r_diff)
# print(errors)

# Plot results
# plt.figure(figsize=(10, 6))
# plt.imshow(errors, extent=[var_m.min(), var_m.max(), var_r.min()*1e6, var_r.max()*1e6],
#            aspect='auto', origin='lower', cmap='viridis')
# plt.colorbar(label='Localization Error (pixels)')
# plt.xlabel('Magnification (M)')
# plt.ylabel('Particle Radius (µm)')
# plt.title('Localization Error for Different Radii and Magnifications')
# plt.show()