import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt


def process_spectrometer_data(filename):
    # Define the base directory where the files are located
    base_dir = 'data'

    # Construct the full path for the input files
    spectral_file_path = os.path.join(base_dir, filename)
    times_file_path = spectral_file_path.replace('.csv', '_times.csv')
    exp_number = int(filename.split('/')[-1][5:10])
    print(exp_number)
    # print(int(a))
    # Read the spectral data file
    spectral_data = pd.read_csv(spectral_file_path, header=None)

    # print(len(spectral_data))
    # Extract the indices (first row) and wavelengths (second row)
    indices = spectral_data.iloc[0, 1:].values
    # print(indices)
    wavelengths = spectral_data.iloc[1, 0:].values
    spectral_densities = spectral_data.iloc[2:, 0:].values  # Exclude the first column (index) and first two rows
    # print(len(spectral_densities))
    first_spectral_density = spectral_densities[0, :]
    adjusted_spectral_densities = spectral_densities - first_spectral_density
    # spectral_density_dark = spectral_densities[0]
    max_spectral_density = adjusted_spectral_densities.max()

    # Read the times file
    with open(times_file_path, 'r') as times_file:
        times_line = times_file.readlines()  # Read the second line
    # print(times_line[3])
    times = times_line[2:]  # Get all times starting from the third value

    # Convert times to datetime objects
    times_datetime = [datetime.fromisoformat(time_str.strip()) for time_str in times]

    # Reference time (fourth time entry)
    reference_time = times_datetime[1]

    # Calculate time differences in milliseconds
    time_deltas = [(time - reference_time).total_seconds() * 1000 for time in times_datetime]
    print(len(time_deltas))



    for time_i in range(len(spectral_densities)):
        plt.plot(wavelengths, adjusted_spectral_densities[time_i])
        plt.plot(wavelengths, spectral_densities[time_i])
        # plt.plot(t, phase_diff)
        plt.xlabel('Lambda, nm')
        plt.ylabel('Counts')
        plt.title(f'Spectral density, Exp {exp_number}, t={round(time_deltas[time_i])}')
        # plt.ylim(0, max_spectral_density)
        # plt.legend(['original', 'deconstructed'])
        plt.show()

        plt.close()
    return True
    #
    # return {
    #     'indices': indices,
    #     'wavelengths': wavelengths,
    #     'spectral_densities': spectral_densities,
    #     'time_deltas': time_deltas
    # }


if __name__ == '__main__':
    # Example usage
    filename = "CMFX_01038_spectrometerSR200584.csv"
    # filename = "CMFX_01212_spectrometerUSB2G410.csv"
    # filename = "tests/CMFX_00206_spectrometerSR200584.csv"
    data = process_spectrometer_data(filename)

    # print("Indices:", data['indices'])
    # print("Wavelengths (nm):", data['wavelengths'])
    # print("Spectral Densities:", data['spectral_densities'])
    # print("Time Deltas (ms):", data['time_deltas'])
