import pandas as pd
import sqlite3
import warnings
import os
warnings.filterwarnings("ignore")

current_directory = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_directory, 'data')

# Read the data
def load_data():
    df = pd.read_csv(os.path.join(data_path, 'dados-abertos.csv'), sep=';')
    return df

# Get the data
df = load_data()
# Clean the data
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
# Create the database
conn = sqlite3.connect(os.path.join(data_path, 'covid_data.db'))
# Create the table
df.to_sql('historical_data', conn, if_exists='replace', index=False)
# Close the connection
conn.commit()
conn.close()

