import pandas as pd
import sqlite3
import warnings
warnings.filterwarnings("ignore")

# Read the data
def load_data():
    df = pd.read_csv('../data/dados-abertos.csv', sep=';')
    return df

# Get the data
df = load_data()
# Clean the data
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
# Create the database
conn = sqlite3.connect('../data/covid_data.db')
# Create the table
df.to_sql('historical_data', conn, if_exists='replace', index=False)
# Close the connection
conn.commit()
conn.close()

