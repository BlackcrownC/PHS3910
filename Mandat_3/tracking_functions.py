import numpy as np
import pandas as pd
import trackpy as tp
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from avi_to_3Darray import video_to_3d_array

from Loc_func import super_locs

# Parameters for plotting
plt.rcParams.update({'font.size': 15})
plt.rcParams.update({'figure.figsize': (8, 6)})
plt.rcParams.update({'figure.dpi': 100})
plt.rcParams.update({'axes.grid': True})


def create_dataframe_from_positions(frames, resample_factor):
    """
    Create a pandas DataFrame from video frames by extracting positions of localizations.
    Parameters:
        - frames (numpy.ndarray): A 3D numpy array representing video frames.
        - resample_factor (int): The factor by which to resample the frames.
    Returns:
        - pandas.DataFrame: The DataFrame has the following columns:
            - 'x': x positions of localizations.
            - 'y': y positions of localizations.
            - 'frame': Frame numbers corresponding to each localization.
    """
    video_array_resample = frames[::resample_factor,:,:]
    x_positions = []
    y_positions = []
    frames = []
    for i in range(video_array_resample.shape[0]):
        x, y = super_locs(video_array_resample[i,:,:],intensity_threshold=250,dist_threshold=50, plot=False)
        number_of_localizations = len(x)
        print(f"Number of localizations for frame {i}: {number_of_localizations}")
        x_positions.extend(x)
        y_positions.extend(y)
        frames.extend([i]*number_of_localizations)

    dicto = {'x':x_positions,
             'y':y_positions,
             'frame':frames}
        
    df = pd.DataFrame(dicto)

    return df

def link_particules(df, search_range=10, min_frames=15):
    """
    Link localizations in a DataFrame to form trajectories.
    Parameters:
        - df (pandas.DataFrame): A DataFrame containing columns 'x', 'y', and 'frame'.
        - search_range (int): The maximum distance between two localizations for them to be linked.
    Returns:
        - pandas.DataFrame: The DataFrame has the following columns:
            - 'x': x positions of localizations.
            - 'y': y positions of localizations.
            - 'frame': Frame numbers corresponding to each localization.
            - 'particle': Trajectory number corresponding to each localization.
    """
    # Perform the tracking
    tracked = tp.link(df, search_range)  # Adjust search_range

    #remove track with less than 'min_frames' localizations
    tracked = tp.filter_stubs(tracked, min_frames)

    return tracked


def adjust_trajectories(tracked, particle_list):
    for particle in particle_list:
        x_before_adjust = np.array(tracked[tracked['particle'] == particle]['x'])
        y_before_adjust = np.array(tracked[tracked['particle'] == particle]['y'])
        t = np.array(tracked[tracked['particle'] == particle]['frame'])

        reg_x = LinearRegression().fit(t.reshape(-1, 1), x_before_adjust)
        reg_y = LinearRegression().fit(t.reshape(-1, 1), y_before_adjust)

        x_adjusted = x_before_adjust - reg_x.predict(t.reshape(-1, 1))
        y_ajusted = y_before_adjust - reg_y.predict(t.reshape(-1, 1))

        tracked.loc[tracked['particle'] == particle, 'x'] = x_adjusted
        tracked.loc[tracked['particle'] == particle, 'y'] = y_ajusted
    return tracked

def calculate_radius(tracked, particle_list, time_lag=5):
    # Constants
    kb = 1.38e-23 # J/K
    T = 20 + 273 # K
    n = 1.0016e-3
    pixel_size = 3.45e-6 # m
    fps = 33
    resampling = 4
    M = 4

    m_convertion = 1/resampling*fps*pixel_size**2/M

    r_list = []
    for particule in particle_list:
        x_positions = np.array(tracked[tracked['particle'] == particule]['x'])
        y_positions = np.array(tracked[tracked['particle'] == particule]['y'])
        #t = np.array(tracked[tracked['particle'] == particule]['frame'])

        # Calculate the MSD for different time lags
        msd = []
        time_lags = np.arange(1, time_lag+1)

        for time_lag in time_lags:
            x_lag = x_positions[:-time_lag]
            y_lag = y_positions[:-time_lag]
            x_lead = x_positions[time_lag:]
            y_lead = y_positions[time_lag:]
            
            msd.append(np.sum(np.mean((x_lead - x_lag)**2) + np.mean((y_lead - y_lag)**2)))

        # fit a line to the MSD
        reg = LinearRegression().fit(time_lags.reshape(-1, 1), msd)
        r = 2*kb*T/(3*np.pi*n*reg.coef_[0]*m_convertion)
        if r > 0:
            r_list.append(r)
            print(f"Radius of the particle {particule}: {r:.2e} m")

        # plot the MSD every 3 frames
        if particule % 3 == 0:
            plt.plot(time_lags, msd, 'o', label=f'Particle {particule}')
            plt.plot(time_lags, reg.predict(time_lags.reshape(-1, 1)), label=f'Fit for particle {particule}')
            plt.xlabel('Time lag')
            plt.ylabel('MSD')
            plt.legend()
            plt.show()

    return r_list

def procedure_with_dataframe(dataframe_path):
    # Load the DataFrame
    df = pd.read_pickle(dataframe_path)

    # Link the localizations to form trajectories
    tracked = link_particules(df, search_range=10)
    tp.plot_traj(tracked, label=True)
    plt.show()

    # Adjust the trajectories
    tracked = adjust_trajectories(tracked, tracked['particle'].unique())
    tp.plot_traj(tracked, label=True)
    plt.show()

    # Calculate the radius of the particles
    r_list = calculate_radius(tracked, tracked['particle'].unique())

    return r_list

def main_procedure(video_path, resample_factor, time_lag):
    # Load the video
    print(f"Loading video from {video_path}...")
    video_array = video_to_3d_array(video_path)

    # Create a DataFrame from the video frames
    print("Creating DataFrame from video frames...")
    df = create_dataframe_from_positions(video_array, resample_factor)

    # Link the localizations to form trajectories
    print("Linking localizations to form trajectories...")
    tracked = link_particules(df, search_range=10)
    tp.plot_traj(tracked, label=True)
    plt.show()

    # Adjust the trajectories
    print("Adjusting the trajectories to compensate for drift...")
    tracked = adjust_trajectories(tracked, tracked['particle'].unique())
    tp.plot_traj(tracked, label=True)
    plt.show()

    # Calculate the radius of the particles
    print("Calculating the radius of the particles...")
    r_list = calculate_radius(tracked, tracked['particle'].unique(), time_lag)

    print(f"Mean radius: {np.mean(r_list):.2e} m")

# Test from a saved DataFrame (quicker)
r_list = procedure_with_dataframe(r'Mandat_3\dataframe.pkl')
print(np.mean(r_list))

# Main procedure starting from the video in .avi format
#main_procedure('Mandat_3/video_to_start_coding_2.avi', resample_factor=4, time_lag=5)
