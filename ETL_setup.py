import logging 
import requests
import pandas as pd 
import mysql.connector
from sqlalchemy import create_engine
import sys
import os

def main():

    url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
    output_file_name = 'owid-covid-data.csv'
    cleaned_csv = 'cleaned_covid_data.csv'

    check_if_history_file_exists()
    pull_data(url, output_file_name)
    clean_data(output_file_name)
    connect_to_MySQL()
    import_csv_to_MySQL(cleaned_csv)
    query_table_for_tableau()
    create_history_log()

def check_if_history_file_exists():
    
    print('\tChecking if file history log exists in this directory')

    if os.path.exists('file_history.log'):
        print('\t\tA History log exists.')
        print('\t\tWould you like to delete it? (yes or no)')
        
        while True:

            answer = input('\t\tyes or no: ')
            if answer == 'yes':
                os.remove('file_history.log')
                print('\t\tHistory log removed.')
                return False

            elif answer == 'no':
                print('\t\tPlease rename the existing log to something other than "file_history.log".')
                print('\t\tPlease rerun the script after completing the rename.')
                sys.exit()

            else:
                print('\t\tIncorrect answer. Please choose "yes" or "no"')           

def pull_data(url, output_file_name):

    print('\tPulling COVID-19 DATA (CSV file)')
    with requests.get(url) as rq:
        with open(output_file_name, 'wb') as file:
            file.write(rq.content)

def clean_data(output_file_name):
    
    print('\tCleaning Data')

    # create dataframe for csv file 
    df = pd.read_csv(output_file_name)

    # convert `date` into a datetime data type 
    df['date'] = pd.to_datetime(df['date'])

    # Replacing all df['new_cases'] NaN values with 0 
    df['new_cases'] = df['new_cases'].fillna(0)

    # Replacing all df['new_deaths'] NaN values with 0 
    df['new_deaths'] = df['new_deaths'].fillna(0)

    # Replacing all location named Oceania to Australia
    df['location'] = df['location'].apply(lambda x: x.replace('Oceania', 'Australia'))

    # Filter out necessary columns 
    df = df[['iso_code', 'continent', 'location', 'date', 'population', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']]

    # Convert df into csv file
    df.to_csv('cleaned_covid_data.csv', header=True, index=False)

def connect_to_MySQL():
    
    print('\tConnecting to MySQL')
    # Connecting to MySQL
    try:

        global username 
        username = input('\tPlease enter MySQL username: ')
    
        global password 
        password = input('\tPlease enter MYSQL password: ')
    
        db = mysql.connector.connect(
             user=username,
             passwd=password)

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

def import_csv_to_MySQL(cleaned_csv):
    # Import Cleaned CSV to MySQL
    # Make sure you are in the correct directory when running the script 

    # SQLalchemy connection to MySQL
    engine = create_engine(f'mysql+pymysql://{username}:{password}@localhost:3306/COVID_ETL_PIPELINE') 

    print('\tImporting Cleaned CSV to MySQL')
    df = pd.read_csv(cleaned_csv) 
    df.to_sql('covid_19_data',con=engine,index=False, if_exists='append')
    print('\tImport Completed')

def query_table_for_tableau():
    # Create table needed for Tableau Dashboard 

    print('\tCreating Table for Tableau Dashboard')
    db = mysql.connector.connect(
         user=username,
         passwd=password)

    mycursor = db.cursor()

    mycursor.execute('USE covid_etl_pipeline')
    mycursor.execute('DROP TABLE IF EXISTS Total_Cases_Per_Continent')
    mycursor.execute('CREATE TABLE Total_Cases_Per_Continent (date date,location varchar(255),cumulative_cases numeric)') 
    mycursor.execute('INSERT INTO Total_Cases_Per_Continent SELECT date, location, SUM(new_cases) OVER w AS cumulative_cases FROM covid_19_data WHERE location IN ("Europe", "South America", "North America", "Africa", "Australia", "Asia") WINDOW w AS (PARTITION BY location ORDER BY date)')       
    db.commit()                    

def create_history_log():
    
    # Configure Logging 
    logging.basicConfig(filename='file_history.log', level=logging.INFO,
                        format='%(levelname)s:%(message)s on %(asctime)s')

    # Create History Log
    logging.info('First Extract of COVID-19 Data')
    print('\tInitial History Log Created')

if __name__ == '__main__':
    main()