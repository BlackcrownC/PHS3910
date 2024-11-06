import pandas as pd
import matplotlib.pyplot as plt

# Load metrics from the CSV file
df = pd.read_csv(r'C:\Users\pageo\Documents\PHS3910\metrics.csv')

# Get the data from the DataFrame
combinations = df['Combinasion of parameters']
resolution = df['Mean resolution (mm)']
resolution_uncertainty = df['Resolution uncertainty (mm)']
contrast = df['Mean contrast (mm)']
contrast_uncertainty = df['Contrast uncertainty (mm)']

### Plotting the resolution

# Create a bar plot with error bars
plt.figure(figsize=(10, 6))  
plt.bar(combinations, resolution, yerr=resolution_uncertainty, capsize=5, color='skyblue')
plt.xticks(rotation=45, ha='right') 
plt.ylabel('Resolution (mm)')  
plt.title('Resolution with uncertainty for different parameter combinations')
plt.tight_layout()
plt.show()

### Plotting the contrast

# Create a bar plot with error bars
plt.figure(figsize=(10, 6))  
plt.bar(combinations, contrast, yerr=contrast_uncertainty, capsize=5, color='skyblue')
plt.xticks(rotation=45, ha='right')  
plt.ylabel('Contrast') 
plt.title('Contrast with uncertainty for different parameter combinations') 
plt.tight_layout()
plt.show()

