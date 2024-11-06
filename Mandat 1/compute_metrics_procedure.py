from get_metrics import get_metrics, load_from_mat
import numpy as np
import os
import csv

# Process the correlation matrices and calculate the metrics

# Define the mapping for the materials
mat = {
        'pin' : 'Pin',
        'plexi' : 'Plexi',
        'pvc' : 'PVC',
}

folder_path = 'Mandat 1\corr_map_2'

data = [
    ['Combinasion of parameters', 'Mean resolution (mm)', 'Resolution uncertainty (mm)', 'Mean contrast (mm)', 'Contrast uncertainty (mm)'],
    ]

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.mat') and os.path.isfile(os.path.join(folder_path, filename)):
        print(f'Processing {filename}...')
        filename_without_ext = os.path.splitext(filename)[0]

        # Load the correlation matrix
        corr_matrices = load_from_mat(os.path.join(folder_path, filename))
        print(f'{filename_without_ext} loaded')
        contrast_list = []
        resolution_list = []

        try:
            # Calculate the metrics
            for i in range(corr_matrices.shape[2]):
                corr_mat = corr_matrices[:,:,i]
                resolution, contrast = get_metrics(corr_mat)
                print('Done')
                resolution_list.append(resolution)
                contrast_list.append(contrast)
            
            mean_contrast = np.mean(contrast_list)
            std_contrast = np.std(contrast_list)
            contrast_uncertainty = std_contrast / np.sqrt(len(contrast_list))

            mean_resolution = np.mean(resolution_list)
            std_resolution = np.std(resolution_list)
            resolution_uncertainty = std_resolution / np.sqrt(len(resolution_list))

            mat_name, forme_name, sensor = filename_without_ext.split('_')

            data.append([f'{mat[mat_name]}, {forme_name} et position {sensor}', mean_resolution, resolution_uncertainty, mean_contrast, contrast_uncertainty])
            print('-'*50)

        except Exception as e:
            print(f'Error processing {filename}: {e}')
            print('-'*50)
            
# Open the file in write mode and write the data
with open('metrics.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write each row of data
    writer.writerows(data)






