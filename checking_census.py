import pandas as pd
import os

# Set the directory where the CSV files are located
directory = 'NC_Census_2021'

# Read table01.csv into a dataframe only keep the first column
full_df = pd.read_csv(os.path.join(directory, 'table01.csv'), usecols=[0])

# Loop through each file in the directory and read it into a dataframe
for filename in os.listdir(directory):
    if filename.startswith('table') and filename.endswith('.csv'):
        # Read the CSV file into a dataframe
        df = pd.read_csv(os.path.join(directory, filename))
        # Only keep the first and second columns
        df = df.iloc[:, :2]
        # Rename the second column to the filename
        df.rename(columns={df.columns[1]: filename}, inplace=True)

        # Join the dataframe to the existing full_df on the first column
        full_df = full_df.join(df.set_index(df.columns[0]), on=full_df.columns[0])

# Rename the columns
full_df.rename(columns={full_df.columns[0]: 'County'}, inplace=True)

print(full_df.head())

'''
Conclusion: the census level data does not in fact have consistent population figures across Totals
'''