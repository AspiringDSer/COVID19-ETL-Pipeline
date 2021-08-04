### This script is used to check if the COVID-19 Data is up to date. ###
### If updated -> Return message that data is updated.               ###
### If NOT updated -> Repeat steps in "ETL_setup.py"                 ###

# Import Necessary Libraries 
from datetime import date
import logging 
import requests
import pandas as pd 
import sys
from ETL_setup import clean_data, connect_to_MySQL,import_csv_to_MySQL, query_table_for_tableau

def main():

    output_file_name = 'owid-covid-data.csv'
    cleaned_csv = 'cleaned_covid_data.csv'
    file_history_df = convert_filelog_to_df()

    convert_filelog_to_df()
    check_files_updated(file_history_df)
    clean_data(output_file_name)
    connect_to_MySQL()
    import_csv_to_MySQL(cleaned_csv)
    query_table_for_tableau()
    create_history_log()


# Check if files are up to date 
# Convert file_history.log to dataframe 

def convert_filelog_to_df(file_history = 'file_history.log'):

    # load in file 
    file = open(file_history, 'r')
    temp = file.read()

    # split on line space
    history = temp.split('\n')

    # create dataframe
    log_history_df = pd.DataFrame()
    log_history_df['Log History'] = history

    # removes empty last row 
    log_history_df = log_history_df[:-1]

    #create empty lists
    log_status = []
    log_date = []
    log_time = []

    # loop though each element in each row 
    for element in log_history_df['Log History']:
    
        # get log status
        log_status.append(element.split(' on')[0].split(':')[1])
    
        # get log date
        log_date.append(element.split('on ')[1].split(' ')[0])

        # get log time 
        log_time.append(element.split('on ')[1].split(' ')[1])
    
    # update dataframe  
    log_history_df['Log Status'] = log_status
    log_history_df['Log Date'] = log_date
    log_history_df['Log Time'] = log_time
    log_history_df = log_history_df.drop('Log History', axis=1)
    
    return log_history_df

# Check if files are updated by comparing the last pull timestamp with current date 
# Files are updated daily. 
def check_files_updated(history_log_df):

    # Check if Files are already updated, files are updated daily 

    today = date.today()
    check_date = today.strftime('%Y-%m-%d')

    if check_date == history_log_df['Log Date'].iloc[-1]:
        print('COVID-19 data is already up to date.')
        print('Please wait for tomorrow for updates.')
        sys.exit()
        

    else:
        print('\tPulling Updated COVID-19 DATA (CSV file)')
        with requests.get('https://covid.ourworldindata.org/data/owid-covid-data.csv') as rq:
            with open('owid-covid-data.csv', 'wb') as file:
                file.write(rq.content)

def create_history_log():
    
    # Configure Logging 
    logging.basicConfig(filename='file_history.log', level=logging.INFO,
                        format='%(levelname)s:%(message)s on %(asctime)s')

    # Create History Log
    logging.info('Successfully Updated COVID-19 Data')
    print('\tSuccessfully Updated COVID-19 Data')

if __name__ == '__main__':
    main()