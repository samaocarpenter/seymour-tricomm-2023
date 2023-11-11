import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas dataframe
df = pd.read_csv('NC_Census_2021/table01.csv')

# Plot a histogram for each column in the dataframe
for col in df.columns:
    plt.hist(df[col])
    plt.title(col)
    plt.show()
