import sys
import datetime
import subprocess
import os
import tarfile
import gzip
from datetime import datetime, timedelta
import csv
import pandas as pd
from pathlib import Path

# General script settings
toMilliseconds = 60 * 1000
#-----------------------------------------------------------------------------
# Settings 2: Raw JTL File Name and offset settings
# Original jtl file and its S3 path
#fullRawJTL_fileName='ContentAPI_30thJune2023_ReleaseV2.jtl'
# Steady State Duration
steady_state_duration = 45 * toMilliseconds # in Minutes
# Number of Reports, Load Names and startTime_offsets in minutes
load_names = ['1X']
load_offsets_inMinutes = [15]
#fullRawJTL_fileName = 'PMC_R52_Aggregate_BTS_Others_20231130-044737.csv'
#fullRawJTL_fileName = 'PMC_R52_Aggregate_BTS_P+_20231130-044850.csv'
#fullRawJTL_fileName = 'PMC_R51_APAC_AU_NZ_Clinical_20231129_03.csv'
#fullRawJTL_fileName = 'PMC_R52_Aggregate_Normal_20231130-013823.csv'
#fullRawJTL_fileName = 'PMC_R52_APAC_AU_NZ_Clinical_20231129_02.csv'
#fullRawJTL_fileName = 'PMC_R52_Normal_Aggregate_20231205-120420.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231205-214137.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231205-214124.csv'
#fullRawJTL_fileName = 'PMC_R52_Normal_Aggregate_20231206-184018.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231206-202603.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231206-202604.csv'
#fullRawJTL_fileName = 'PMC_R52_Normal_Aggregate_20231207-205436.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231207-220241.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231207-220230.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231211-230603.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231211-230609.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231212-092049.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231212-105210.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231212-105152.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231212-092047.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_Others_Aggregate_20231212-074230.csv'
#fullRawJTL_fileName = 'PMC_R52_BTS_P+_Aggregate_20231212-074224.csv'
#fullRawJTL_fileName = 'PMC_R52_SpBTS_Aggregate_20231212-214434.csv'
#fullRawJTL_fileName = 'PMC_R52_SpBTS_Aggregate_20231213-034736.csv'
#fullRawJTL_fileName = 'PMC_R53_SpringBTS_Aggregate_20240108-194229.csv'
fullRawJTL_fileName = 'PMC_R53_SpringBTS_Aggregate_20240109-181710.csv'

rawJTL_fileDownload_localpath = 'C:/Users/VRATNSI/Downloads/PMC/Results/JMeterScripts/Results/'
#rawJTL_fileDownload_localpath = 'C:/Users/VRATNSI/Downloads/ContentAPI_30thJune2023_ReleaseV2/'
jmeter_path = 'C:\\Users\\VRATNSI\\Downloads\\apache-jmeter-5.5\\apache-jmeter-5.5\\bin\\'
filteredJTL_fileDownload_localpath = rawJTL_fileDownload_localpath
filteredJTL_fileDownload_localpath_win = filteredJTL_fileDownload_localpath.replace('/', '\\')


file_name = fullRawJTL_fileName
report_number = '1'

fullRawJTL_fileNameNpath = rawJTL_fileDownload_localpath + fullRawJTL_fileName

# Function to filter raw JTL File
def filter_file_content(file_path, start_time, steady_state_duration, fileNumber):
    # Open the source file for reading
    with open(file_path, 'r') as source_file:
        # Read the contents of the source file
        content = source_file.readlines()
    # Copy header and Remove it
    header = content[0]
    content = content[1:]
    # Sort the contents based on timestamp
    sorted_content = sorted(content)
    # Get the first and last timestamp in milliseconds
    first_timestamp = int(sorted_content[0].split(",")[0])
    last_timestamp = int(sorted_content[-1].split(",")[0])
    Slicetime_after_first = first_timestamp + start_time
    Slicetime_before_last = Slicetime_after_first + steady_state_duration
    print("Starting timestamp of original JTL File:", datetime.fromtimestamp(first_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print("Ending timestamp of original JTL File:", datetime.fromtimestamp(last_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print("Timestamp of filtered "+fileNumber+"X JTL File:")
    #Timestamp in EST
    print("In EST","Start:", datetime.fromtimestamp(Slicetime_after_first / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "End:", datetime.fromtimestamp(Slicetime_before_last / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    #Timestamp in UTC
    print("In UTC","Start:", datetime.utcfromtimestamp(Slicetime_after_first / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], "End:", datetime.utcfromtimestamp(Slicetime_before_last / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    #print("Ending timestamp of filtered "+fileNumber+"X JTL File:", datetime.datetime.fromtimestamp(Slicetime_before_last / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])   
    # System Error if ramping time not within input window
    if Slicetime_after_first > last_timestamp or Slicetime_before_last < first_timestamp:
        sys.exit("Error: Ramping time not within input window")

    # Find row number with timestamp according to the conditions
    for i in range(len(sorted_content)):
        if int(sorted_content[i].split(",")[0]) > Slicetime_after_first:
            first_row = i
            break
    for i in reversed(range(len(sorted_content))):
        if int(sorted_content[i].split(",")[0]) < Slicetime_before_last:
            last_row = i
            break
    filtered_content = sorted_content[first_row:last_row + 1]
    print("Length of original RAW Jtl content:", len(content))
    print("Length of filtered "+fileNumber+"X content:", len(filtered_content))

    return header, filtered_content

def filterTransactions_and_save_csv(input_file, output_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)
    
    # Create a dictionary to store filtered DataFrames
    filtered_dfs = {}
    
    start_keywords = ['PMC']
    end_keywords = ['OrderHistory', 'Home', 'Create']
    
    # Filter rows where the 'label' column starts with 'PMC'
    filtered_df = df[df['label'].str.startswith('PMC')]
    # Save the filtered DataFrame along with the header to a new CSV file
    filtered_df.to_csv(output_file, index=False)
    
    # Open the output file and write the header
    #with open(output_file, 'w') as file:
    #    header = ','.join(filtered_df.columns) + '\n'
    #    file.write(header)
    #
    #    # Write the filtered rows
    #    for _, row in filtered_df.iterrows():
    #        line = ','.join(map(str, row.values)) + '\n'
    #        file.write(line)
    
    # Display the filtered DataFrame (optional)
    print(filtered_df)



#-----------------------------------------------------------------------------
# Main Code
#-----------------------------------------------------------------------------
# Define the report settings using a loop
report_settings = []
for i in range(len(load_names)):
    load_name = load_names[i]
    load_offset = load_offsets_inMinutes[i]
    start_time = load_offset * toMilliseconds
    filtered_file_name = f'{fullRawJTL_fileName}_filtered_{load_name.lower()}.csv'
    trx_filtered_file_name = f'{fullRawJTL_fileName}_TRXfiltered_{load_name.lower()}.csv'
    report_settings.append({
        'startTime': start_time,
        'fileName': filtered_file_name,
        'trxFiltered_file_name': trx_filtered_file_name,
        'reportNumber': str(i + 1)
    })

#-----------------------------------------------------------------------------
# Filter the raw jtl file content and generate graphs, reports for each report
for settings in report_settings:
    start_time = settings['startTime']
    filtered_file_name = settings['fileName']
    trx_filtered_file_name = settings['trxFiltered_file_name']
    report_number = settings['reportNumber']

    # Filter the file content
    header, filtered_content = filter_file_content(fullRawJTL_fileNameNpath, start_time, steady_state_duration, report_number)

    # Write the filtered content to the output jtl file
    filtered_file_path = filteredJTL_fileDownload_localpath + filtered_file_name
    with open(filtered_file_path, 'w') as output_file:
        output_file.write(header)
        output_file.writelines(filtered_content)
    
    #Filtering specific Trx only
    TRX_filtered_file_path = filteredJTL_fileDownload_localpath + trx_filtered_file_name
    print(filtered_file_path)
    df = pd.read_csv(filtered_file_path)
    print(df)
    print(TRX_filtered_file_path)
    filterTransactions_and_save_csv(filtered_file_path,TRX_filtered_file_path)
