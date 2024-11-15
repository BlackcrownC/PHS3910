import numpy as np
import os
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import skewnorm

def create_correlation_bank(correlation_folder_path):
    """
    Create a dictionary of correlation signals from a folder of correlation signals.

    This function reads all the correlation signals in a folder and creates a dictionary of the signals.

    Parameters:
    correlation_folder_path (str): The path to the folder containing the correlation signals.

    Returns:
    dict: A dictionary of correlation signals, where the keys are the names of the signals and the values are the signals themselves.
    """
    correlation_bank = {}
    for key_name in os.listdir(correlation_folder_path):
            correlation_bank[f'{key_name}'] = np.load(f'{correlation_folder_path}/{key_name}/1.npy', allow_pickle=True)
    return correlation_bank

def get_signals(signals_folder_path):
    """ 
    Create a dictionary of signals from a folder of signals.
    
    This function reads all the signals in a folder and creates a dictionary of the signals.
    
    Parameters:
    signals_folder_path (str): The path to the folder containing the signals.  

    Returns:
    dict: A dictionary of signals, where the keys are the names of the signals and the values are the signals themselves.
    """
    signals = {}
    for try_ in os.listdir(signals_folder_path):
        signals[f'{try_}'] = np.load(f'{signals_folder_path}/{try_}/1.npy', allow_pickle=True)
    return signals

def key_name_to_x_position(key_name):
    """
    Convert a key name to its corresponding x position on the piano keyboard.

    This function converts a key name to its corresponding x position [cm] on the piano keyboard.

    Parameters:
    key_name (str): The name of the key.

    Returns:
    int: The x position [cm] of the key on the piano keyboard.
    """
    conversion = {
                "C4_1": 0.75,
                "C4_2": 2.25,
                "D4_1": 3.75,
                "D4_2": 5.25,
                "E4_1": 6.75,
                "E4_2": 8.25,
                "F4_1": 9.75,
                "F4_2": 11.25,
                "G4_1": 12.75,
                "G4_2": 14.25,
                "A5_1": 15.75,
                "A5_2": 17.25,
                "B5_1": 18.75,
                "B5_2": 20.25,
                "C5_1": 21.75,
                "C5_2": 23.25,
                }
        
    return conversion[key_name]

def correlate_two_signals(signal1, signal2):
    """
    Calculate the maximum correlation between two signals.

    This function computes the cross-correlation of two input signals and returns the maximum value of the correlation.

    Parameters:
    signal1 (array-like): The first input signal.
    signal2 (array-like): The second input signal.

    Returns:
    float: The maximum value of the cross-correlation between the two signals.
    """
    correlation = np.correlate(signal1/ np.linalg.norm(signal1), signal2/ np.linalg.norm(signal2), 'same')
    max_corr = np.max(correlation)
    return max_corr

def correlate_signal_to_bank(signal, note, correlation_bank):
    """
    Correlates a given signal with a bank of signals and returns the correlation coefficients.

    Args:
        signal (list or array-like): The signal to be correlated.
        correlation_bank (dict): A dictionary where keys are signal names and values are the signals to correlate with.

    Returns:
        list of tuples: A list of tuples where each tuple contains the x-position (derived from the key name) 
                        and the maximum correlation coefficient for the corresponding signal in the correlation bank.
    """
    correlation_coefficients = {}
    for key_name in correlation_bank:
        max_corr = correlate_two_signals(signal, correlation_bank[key_name])
        correlation_coefficients[key_name] = max_corr
        #correlation_coefficients.append((key_name, max_corr))

    max_note = max(correlation_coefficients, key=correlation_coefficients.get)

    correlation_coefficients = {key_name_to_x_position(key_name): max_corr for key_name, max_corr in correlation_coefficients.items()}

    is_good_note = bool(max_note == note)

    return correlation_coefficients, is_good_note

def calculate_metrics(correlation_coefficients):
    """
    Calculate the Full Width at Half Maximum (FWHM) and contrast from a set of correlation coefficients.
    This function fits a Gaussian curve to the provided correlation coefficients and calculates the FWHM
    and contrast of the fitted curve. The results are then plotted.
    Parameters:
    correlation_coefficients (list of tuples): A list of tuples where each tuple contains two elements:
                                               the position on the piano keyboard (x) and the corresponding
                                               correlation coefficient (y).
    Returns:
    tuple: A tuple containing:
        - FWHM (float): The Full Width at Half Maximum of the fitted Gaussian curve.
                            and the mean of the correlation coefficients that are less than half of the maximum.
    """


    def gaussian(x, amp, mu, sigma):
        return amp * np.exp(-(x - mu)**2 / (2 * sigma**2))
    
    # make arrays with the x positions and correlation coefficients
    x_position = np.array(list(correlation_coefficients.keys()))
    corr_coef = np.array(list(correlation_coefficients.values()))
    # calculate contrast
    maximum_correlation = max(corr_coef)
    threshold = 0.5 * maximum_correlation
    noise = corr_coef[corr_coef < threshold]
    baseline = np.mean(noise)
    contrast = maximum_correlation - baseline

    corr_coef = corr_coef - baseline


    lower_bounds = (0, 0, 0)
    upper_bounds = (np.max(corr_coef), 24, 12)
    popt, _ = curve_fit(gaussian, x_position, corr_coef, p0=[np.max(corr_coef), x_position[np.argmax(corr_coef)], 1], bounds=(lower_bounds, upper_bounds))

    FWHM = 2 * np.sqrt(2 * np.log(2)) * popt[2]

    maximum_correlation = max(corr_coef)
    threshold = 0.5 * maximum_correlation
    noise = corr_coef[corr_coef < threshold]
    baseline = np.mean(noise)
    contrast = maximum_correlation - baseline

    # plt.plot(x_position, corr_coef, 'o', label='Correlation Coefficients')
    # plt.plot(np.linspace(0, 24, 1000), gaussian(np.linspace(0, 24, 1000), *popt), label='Fitted Gaussian Curve')
    # plt.xlabel('Position on the piano keyboard [cm]')
    # plt.ylabel('Correlation Coefficient')
    # #plt.title('Fitted parameters: amplitude = %.2f, mu = %.2f, sigma = %.2f, offset = %.2f' % tuple(popt))
    # plt.legend()
    # plt.grid()
    # plt.show()

    return FWHM, contrast

def main_procedure(correlation_bank, signals):
    resolution_list = []
    contrast_list = []

    for signal_name in signals:
        print(f'Correlate {signal_name} to the bank')
        signal = signals[signal_name]
        correlation_coefficients, is_good_note = correlate_signal_to_bank(signal, signal_name, correlation_bank)
        if is_good_note:
            x = list(correlation_coefficients.keys())
            y = list(correlation_coefficients.values())

            # print('en x', np.any(np.isnan(x)) or np.any(np.isnan(x)))
            # print('en y',  np.any(np.isnan(y)) or np.any(np.isnan(y)))
            try:
                FWHM, contrast = calculate_metrics(correlation_coefficients)
                resolution_list.append(FWHM)
                contrast_list.append(contrast)
            except:
                print('error in calculate_metrics')
    
    print('resolution_list length:', len(resolution_list))
    print('contrast_list length:', len(contrast_list))

    mean_resolution = np.mean(resolution_list)
    mean_contrast = np.mean(contrast_list)

    std_resolution = np.std(resolution_list)
    std_contrast = np.std(contrast_list)

    resolution_uncertainty = std_resolution / np.sqrt(len(resolution_list))
    contrast_uncertainty = std_contrast / np.sqrt(len(contrast_list))

    return mean_resolution, resolution_uncertainty, mean_contrast, contrast_uncertainty

def convert_to_bits(signal, num_bits):
    """
    Convert the signal to a specified number of bits.
    
    Parameters:
    - signal: The input signal (array-like)
    - num_bits: The number of bits to convert the signal to (e.g., 4, 8, 16)
    
    Returns:
    - signal_bits: The signal converted to the specified number of bits
    """
    """
    Encode a 1D signal into a certain number of bits.

    Parameters:
    - signal: np.array, the input signal
    - num_bits: int, the number of bits for quantization

    Returns:
    - quantized_signal: np.array, the quantized signal
    """
    # Calculate the number of quantization levels
    num_levels = 2 ** num_bits

    # Normalize the signal to the range [0, 1]
    min_val = np.min(signal)
    max_val = np.max(signal)
    normalized_signal = (signal - min_val) / (max_val - min_val)

    # Scale to the number of levels and quantize
    quantized_signal = np.round(normalized_signal * (num_levels - 1))

    # Convert to integer type
    quantized_signal = quantized_signal.astype(int)

    return quantized_signal

def change_sampling_freq(data, factor):
    """
    Change the sampling frequency of a signal by a given factor.

    This function changes the sampling frequency of a signal by a given factor.

    Parameters:
    - data: The input signal (array-like)
    - factor: The factor by which to change the sampling frequency (e.g., 2, 4, 10)

    Returns:
    - new_data: The signal with the new sampling frequency
    """
    new_data = data[::factor]
    return new_data[np.isfinite(new_data)]

def low_pass_filter(signal, cutoff_freq, sampling_rate):
    """
    Apply a low-pass filter to a signal using the FFT.

    This function applies a low-pass filter to a signal by performing the following steps:

    Parameters:
    - signal: The input signal to be filtered
    - cutoff_freq: The cutoff frequency for the low-pass filter
    - sampling_rate: The sampling rate of the input signal

    Returns:
    - filtered_signal: The filtered signal after applying the low-pass filter
    """
    # Step 1: Perform the FFT
    fft_signal = np.fft.fft(signal)
    
    # Step 2: Generate frequency bins
    freqs = np.fft.fftfreq(len(signal), 1/sampling_rate)

    # Step 3: Create the low-pass filter mask
    # Allow frequencies below cutoff_freq, zero out others
    filter_mask = np.abs(freqs) <= cutoff_freq
    
    # Step 4: Apply the filter by multiplying the FFT signal by the mask
    filtered_fft_signal = fft_signal * filter_mask

    # Step 5: Perform the inverse FFT to get back to the time domain
    filtered_signal = np.fft.ifft(filtered_fft_signal)
    
    # Return the real part of the inverse FFT (since the signal is real-valued)
    new_data = np.real(filtered_signal)

    return new_data[np.isfinite(new_data)]

if __name__ == "__main__":
    correlation_folder_path = 'correlation'
    correlation_bank = create_correlation_bank(correlation_folder_path)

    #signals_downsampled = {signal_name: change_sampling_freq(signal, factor) for signal_name, signal in signals.items()}
    correlation_bank_downsampled = {key: convert_to_bits(correlation, 32) for key, correlation in correlation_bank.items()}

    signal = np.load(r'signal_test\D4_1\1.npy', allow_pickle=True)
    signal_downsampled = convert_to_bits(signal, 32)

    # check if the is nan of inf in the signal
    print(np.any(np.isnan(signal_downsampled)) or np.any(np.isnan(signal_downsampled)))
    
    correlation_coefficients, is_good_note = correlate_signal_to_bank(signal_downsampled,"F4_1", correlation_bank_downsampled)
    print(is_good_note)
    calculate_metrics(correlation_coefficients)