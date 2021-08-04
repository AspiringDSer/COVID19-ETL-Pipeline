# ETL Pipeline

# The Pipeline is used to extract COVID-19 Data from ourworldindata.org. 
# We are only interested in COVID-19 Cases and Deaths and the respective locations. 

## Initial Setup - Section 1 ##
# 1. Pull COVID-19 Data (CSV file) from ourworldindata.org
# 2. Pulled CSV file will be in the same directory as the script  
# 3. Create History Log
# 4. Clean the Data
# 5. Import Cleaned CSV to MySQL

## Update Data - Section 2 ##
# - Check if data is already if updated, if not, update
# - Update history log 
# - Repeat steps from Import CSV to MySQL

## MySQL to Tableau - Section 3 ##
# Connect MySQL with Tableau 
# Create Tableau Public Dashboard  



# This Python Script will be used to run Section 1 of the ETL Pipeline

# Initial Setup - Section 1 
# Import necessary libraries
import logging 
import requests
import pandas as pd 
import numpy as np
import mysql.connector
from sqlalchemy import create_engine
import sys
from clean_data import clean_data

# Configure Logging 
logging.basicConfig(filename='file_history.log', level=logging.INFO,
                    format='%(levelname)s:%(message)s on %(asctime)s')


### Pull COVID-19 Data (CSV file) from ourworldindata.org ###
### Pulled CSV file will be in the same directory as the script ###

print('\tPulling COVID-19 DATA (CSV file)')
with requests.get('https://covid.ourworldindata.org/data/owid-covid-data.csv') as rq:
    with open('owid-covid-data.csv', 'wb') as file:
        file.write(rq.content)
        
        # Create History Log
        logging.info('First Extract of COVID-19 Data')

csv = 'owid-covid-data.csv'
clean_data(csv)

# ### Clean the Data###
# print('\tCleaning Data')

# # create dataframe for csv file 
# df = pd.read_csv('owid-covid-data.csv')

# # convert `date` into a datetime data type 
# df['date'] = pd.to_datetime(df['date'])

# # Replacing all df['new_cases'] NaN values with 0 
# df['new_cases'] = df['new_cases'].fillna(0)

# # Replacing all df['new_deaths'] NaN values with 0 
# df['new_deaths'] = df['new_deaths'].fillna(0)

# # Replacing all location named Oceania to Australia
# df['location'] = df['location'].apply(lambda x: x.replace('Oceania', 'Australia'))

# # Filter out necessary columns 
# df = df[['iso_code', 'continent', 'location', 'date', 'population', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']]

# # Convert df into csv file
# df.to_csv('cleaned_covid_data.csv', header=True, index=False)

### Import Cleaned CSV to MySQL###

print('\tConnecting to MySQL')
# Connecting to MySQL
username = input('\tPlease enter MySQL username: ')
password = input('\tPlease enter MYSQL password: ')

try:
    db = mysql.connector.connect(
    user=username,
    passwd=password
)
except mysql.connector.errors.ProgrammingError:
    print('\t\tIncorrect username or password')
    print('\t\tPlease rerun script')
    sys.exit()


mycursor = db.cursor()

# Create Database
try:
    mycursor.execute("CREATE DATABASE COVID_ETL_PIPELINE")
except mysql.connector.errors.DatabaseError:
    print('\t\tCOVID_ETL_PIPELINE database already exists')
    print('\t\tWill be overwriting existing covid_19_data table')
    mycursor.execute('USE COVID_ETL_PIPELINE')
    mycursor.execute('DROP TABLE IF EXISTS covid_19_data')
 
# SQLalchemy connection to MySQL
engine = create_engine('mysql+pymysql://root:rootroot@localhost:3306/COVID_ETL_PIPELINE')

# Import Cleaned CSV to MySQL
# Make sure you are in the correct directory when running the script 

print('\tImporting Cleaned CSV to MySQL')
df = pd.read_csv("cleaned_covid_data.csv") 
df.to_sql('covid_19_data',con=engine,index=False, if_exists='append')
print('\tImport Complete')
