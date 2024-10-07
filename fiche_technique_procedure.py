from contrast_and_resolution_1D_functions import (
    main_procedure,
    convert_to_bits,
    change_sampling_freq,
    get_signals,
    create_correlation_bank)

number_of_bits = [16, 12, 8, 5, 4, 3, 2, 1]
sampling_factors = [2, 4, 8, 10, 20, 40, 50, 100]

correlation_folder_path = 'correlation'
signals_folder_path = 'signals' # to create

correlation_bank = create_correlation_bank(correlation_folder_path)
signals = get_signals(signals_folder_path)

results = [
    ['Changes to the signals', 'Mean resolution (mm)',
      'Resolution uncertainty (mm)', 'Mean contrast (mm)',
        'Contrast uncertainty (mm)'],
    ]

# Change the number of bits
for num_bits in number_of_bits:
    print(f'Converting signals to {num_bits} bits...')
    signals_bits = {signal_name: convert_to_bits(signal, num_bits) for signal_name, signal in signals.items()}
    correlation_bank_bits = {key: convert_to_bits(correlation, num_bits) for key, correlation in correlation_bank.items()}

    mean_resolution, resolution_uncertainty, mean_contrast, contrast_uncertainty = main_procedure(correlation_bank_bits, signals_bits)
    results.append([f'Number of bits: {num_bits}', mean_resolution, resolution_uncertainty, mean_contrast, contrast_uncertainty])
    print('-'*50)

# Change the sampling frequency
for factor in sampling_factors:
    print(f'Changing the sampling frequency by a factor of {factor}...')
    signals_downsampled = {signal_name: change_sampling_freq(signal, factor) for signal_name, signal in signals.items()}
    correlation_bank_downsampled = {key: change_sampling_freq(correlation, factor) for key, correlation in correlation_bank.items()}

    mean_resolution, resolution_uncertainty, mean_contrast, contrast_uncertainty = main_procedure(correlation_bank_downsampled, signals_downsampled)
    results.append([f'Sampling frequency factor: {factor}', mean_resolution, resolution_uncertainty, mean_contrast, contrast_uncertainty])
    print('-'*50)

# Change the frequency content