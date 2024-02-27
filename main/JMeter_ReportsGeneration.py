import sys
import datetime
import subprocess
import os
import tarfile
import gzip
import datetime
import csv
import pandas as pd
from pathlib import Path

#-----------------------------------------------------------------------------
# Script Settings
#-----------------------------------------------------------------------------
# Settings 1: Setup AWS, S3 and JMeter settings
# AWS Region
awsRegion='us-east-1'
awsAccountNumber='510779331227'
awsRole='PCMPowerUser'
awsProfile_Region='--profile '+awsRole+'@'+awsAccountNumber+' --region '+awsRegion
application_track = 'PACE'
application = 'ContentAPI'
testObjective = "This is Test Objective"
date = '06302023' #mmddyyyy
#date = datetime.datetime.now()
#date = date.strftime("%m%d%Y")
release = 'Release_v2'

# S3 Perf Testing Reports Bucket Structure
s3path_PerfTestReports_bucket='s3://qecoe-perftestingreports/TestReports/'
s3path_application_track = application_track+'/'
s3path_application = application+'/'
s3path_date_string = date+'/'
s3path_releaseName = release+'/'
#Example: s3://qecoe-perftestingreports/TestReports/PACE/ContentAPI/06302023/Release_v2/raw_results/
s3_fullfilespath = s3path_PerfTestReports_bucket+s3path_application_track+s3path_application+s3path_date_string+s3path_releaseName

# Local destination path and filtered jtl file paths
rawJTL_fileDownload_localpath = 'C:/Users/VRATNSI/Downloads/ContentAPI_30thJune2023_ReleaseV2/'
filteredJTL_fileDownload_localpath = rawJTL_fileDownload_localpath
filteredJTL_fileDownload_localpath_win = filteredJTL_fileDownload_localpath.replace('/', '\\')
jmeter_path = 'C:\\Users\\VRATNSI\\Downloads\\apache-jmeter-5.5\\apache-jmeter-5.5\\bin\\'
# General script settings
toMilliseconds = 60 * 1000
#-----------------------------------------------------------------------------
# Settings 2: Raw JTL File Name and offset settings
# Original jtl file and its S3 path
fullRawJTL_fileName='ContentAPI_30thJune2023_ReleaseV2.jtl'
# Steady State Duration
steady_state_duration = 14 * toMilliseconds # in in Munites
# Number of Reports, Load Names and startTime_offsets in minutes
load_names = ['1X', '2X', '3X', '4X']
load_offsets_inMinutes = [17, 52, 87, 122]
# Filter Transactions List
contentAPI_transactionsList_forReport = ["PUT /narrative-api/narrative/v1/comment/unresolve","GET /assessment-api/assessment/v2/{P_AssessmentVersionURN}"]
# Declare Response Times SLAs in milliseconds
sla_avgResponseTime_values = {'PUT /narrative-api/narrative/v1/comment/unresolve': 3000, 'GET /assessment-api/assessment/v2/{P_AssessmentVersionURN}': 3000}
# Declare Throughput SLAs for the Initial Load level
sla_throughput_values = {'PUT /narrative-api/narrative/v1/comment/unresolve': 100, 'GET /assessment-api/assessment/v2/{P_AssessmentVersionURN}': 102}
#sla_throughput_values = {'PUT /narrative-api/narrative/v1/comment/unresolve': MAX(MAX(Fall 2022), MAX(Spring 2023), MAX(Spring 2022)), 'GET /assessment-api/assessment/v2/{P_AssessmentVersionURN}': 102}

#transactionList = {
#        [{api: 'PUT /narrative-api/narrative/v1/comment/unresolve'
#          responseTimeSLA: 3000
#          trhoughputSLA: 100},
#          {api: 'GET /assessment-api/assessment/v2/{P_AssessmentVersionURN}'
#          responseTimeSLA: 3000
#          trhoughputSLA: 102}
#          ]
#}

#-----------------------------------------------------------------------------
# Settings 3: Script Flags; 0 is False, 1 is True
flag_downloadRawJTlfromS3toLocal = 0
flag_compressJTLs = 0
flag_uploadCompressedJTlsfromlocaltos3 = 0
flag_deleteFilesfromLocal = 1
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# General Functions
#-----------------------------------------------------------------------------
# Function to copy file in/out of S3
def run_aws_s3_cp_command(source_path, destination_path, profile):
    command = f'aws s3 cp {source_path} {destination_path} {profile}'
    try:
        subprocess.run(command, shell=True, check=True)
        print("AWS S3 cp command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the AWS S3 cp command: {e}")
#-----------------------------------------------------------------------------
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
    print("Starting timestamp of original JTL File:", datetime.datetime.fromtimestamp(first_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print("Ending timestamp of original JTL File:", datetime.datetime.fromtimestamp(last_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print("Starting timestamp of filtered "+fileNumber+"X JTL File:", datetime.datetime.fromtimestamp(Slicetime_after_first / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    print("Ending timestamp of filtered "+fileNumber+"X JTL File:", datetime.datetime.fromtimestamp(Slicetime_before_last / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])   
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
#-----------------------------------------------------------------------------
# Functions to generate Graph images and Aggregate CSVs
def generate_individualStats(input_jtl_file_path,filename,report_number):
    atot_graph = f'{jmeter_path}JMeterPluginsCMD.bat --generate-png {input_jtl_file_path}ActiveThreadsOverTime_{report_number}X.png --input-jtl {input_jtl_file_path}{filename} --plugin-type ThreadsStateOverTime --width 1920 --height 1080'
    hps_graph = f'{jmeter_path}JMeterPluginsCMD.bat --generate-png {input_jtl_file_path}HitsPerSecond_{report_number}X.png --input-jtl {input_jtl_file_path}{filename} --plugin-type HitsPerSecond --width 1920 --height 1080'
    rtot_graph = f'{jmeter_path}JMeterPluginsCMD.bat --generate-png {input_jtl_file_path}ResponseTimesOverTime_{report_number}X.png --input-jtl {input_jtl_file_path}{filename} --plugin-type ResponseTimesOverTime --width 2400 --height 1800'
    tps_graph = f'{jmeter_path}JMeterPluginsCMD.bat --generate-png {input_jtl_file_path}TransactionsPerSecond_{report_number}X.png --input-jtl {input_jtl_file_path}{filename} --plugin-type TransactionsPerSecond --width 2400 --height 1800'
    agg_report = f'{jmeter_path}JMeterPluginsCMD.bat --generate-csv {input_jtl_file_path}Aggregate_report_{report_number}X.csv --input-jtl {input_jtl_file_path}{filename} --plugin-type AggregateReport'
    subprocess.run(atot_graph, shell=True)
    subprocess.run(rtot_graph, shell=True)
    subprocess.run(hps_graph, shell=True)
    subprocess.run(tps_graph, shell=True)
    subprocess.run(agg_report, shell=True)
#-----------------------------------------------------------------------------
# Function to tar and gzip
def compress_file(file_path):
    # Create a tar file
    tar_file_path = file_path + '.tar'
    with tarfile.open(tar_file_path, 'w') as tar:
        # Add the text file to the tar file
        tar.add(file_path, arcname=file_path)
    # Create a gzip file
    gz_file_path = tar_file_path + '.gz'
    with open(tar_file_path, 'rb') as tar_file:
        with gzip.open(gz_file_path, 'wb') as gz_file:
            gz_file.writelines(tar_file)

    # Delete the intermediate tar file
    Path(tar_file_path).unlink()
    return gz_file_path
#-----------------------------------------------------------------------------
# Function to delete file
def delete_file(file_path):
    if flag_deleteFilesfromLocal == 1:
        try:
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
        except OSError as e:
            print(f"Error occurred while deleting file '{file_path}': {e}")
#-----------------------------------------------------------------------------
# Function to filter specific transactions from aggregate csvs into a new filtered csv
def filter_csv_by_strings(input_file, output_file, target_strings):
    # Read the original CSV file and filter the desired rows
    filtered_rows = []
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)  # Read the header row
        for row in reader:
            if any(target in row[0] for target in target_strings):
                filtered_rows.append(row)

    # Write the filtered rows along with the header to a new CSV file
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(filtered_rows)

    print(f"Filtered data has been written to '{output_file}'.")
#-----------------------------------------------------------------------------
def filter_dataframe(df, sla_values):
    filtered_df = df[df['Label'].isin(sla_values.keys())].copy()
    return filtered_df
#-----------------------------------------------------------------------------
def add_sla_status(df, sla_values, sla_throughput_values, load):
    for transaction, sla_value in sla_values.items():
        filter_condition = df['Label'] == transaction
        df.loc[filter_condition, 'Response Time SLA Status'] = pd.cut(df.loc[filter_condition, 'Average'], bins=[float('-inf'), sla_value, sla_value*1.1, float('inf')], labels=['Pass', 'Amber', 'Fail'])
        df.loc[filter_condition, 'Throughput SLA Status'] = df.loc[filter_condition, '# Samples'].apply(lambda x: 'Pass' if x >= (int(load) * sla_throughput_values.get(transaction, 0)) else 'Amber' if x >= (0.9 * int(load) * sla_throughput_values.get(transaction, 0)) else 'Fail')
    return df
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
# Main Code
#-----------------------------------------------------------------------------
# Define the report settings using a loop
report_settings = []
for i in range(len(load_names)):
    load_name = load_names[i]
    load_offset = load_offsets_inMinutes[i]
    start_time = load_offset * toMilliseconds
    filtered_file_name = f'filtered_{load_name.lower()}.jtl'
    report_settings.append({
        'startTime': start_time,
        'fileName': filtered_file_name,
        'reportNumber': str(i + 1)
    })
#-----------------------------------------------------------------------------
# Download full raw jtl file from S3 bucket to local
current_path = os.getcwd()
if flag_downloadRawJTlfromS3toLocal == 1:
    s3_rawjtlfilePath = s3_fullfilespath+'raw_results/'+fullRawJTL_fileName
    run_aws_s3_cp_command(s3_rawjtlfilePath, rawJTL_fileDownload_localpath, awsProfile_Region)
fullRawJTL_fileNameNpath = rawJTL_fileDownload_localpath + fullRawJTL_fileName
# Compress original RAW jtl
print('Compression activity file path:', filteredJTL_fileDownload_localpath_win)
text_file_path = filteredJTL_fileDownload_localpath_win + fullRawJTL_fileName
if flag_compressJTLs == 1:
    compressed_file_path = compress_file(text_file_path)
    print('Compressed Original file:', compressed_file_path)
# Upload zipped files into S3 Buckets
if flag_uploadCompressedJTlsfromlocaltos3 == 1:
    run_aws_s3_cp_command(compressed_file_path, s3_fullfilespath+'raw_results/', awsProfile_Region)
#-----------------------------------------------------------------------------
# Filter the raw jtl file content and generate graphs, reports for each report
for settings in report_settings:
    start_time = settings['startTime']
    filtered_file_name = settings['fileName']
    report_number = settings['reportNumber']

    # Filter the file content
    header, filtered_content = filter_file_content(fullRawJTL_fileNameNpath, start_time, steady_state_duration, report_number)

    # Write the filtered content to the output jtl file
    filtered_file_path = filteredJTL_fileDownload_localpath + filtered_file_name
    with open(filtered_file_path, 'w') as output_file:
        output_file.write(header)
        output_file.writelines(filtered_content)

    # Compress Filtered Files
    if flag_compressJTLs == 1:
        compressed_filtered_file_path = compress_file(filtered_file_path)
        print('Compressed Filtered '+report_number+'X file:', compressed_filtered_file_path)

    # Upload Filtered Files and their compressed versions to S3
    if flag_uploadCompressedJTlsfromlocaltos3 == 1:
        #run_aws_s3_cp_command(filtered_file_path, s3_fullfilespath+'Filtered/'+report_number+'X/', awsProfile_Region) # Uncompressed
        run_aws_s3_cp_command(compressed_filtered_file_path, s3_fullfilespath+'Filtered/'+report_number+'X/', awsProfile_Region) # Compressed

    # Generate Graphs and Aggregate CSV from filtered jtl Files
    generate_individualStats(filteredJTL_fileDownload_localpath_win, filtered_file_name, report_number)
    
    # Delete uncompressed filtered files
    delete_file(filtered_file_path)
#-----------------------------------------------------------------------------
print('Path to PNG Files Original file:', filteredJTL_fileDownload_localpath)

for settings in report_settings:
    report_number = settings['reportNumber']

    image_titles = ['ActiveThreadsOverTime', 'HitsPerSecond', 'ResponseTimesOverTime', 'TransactionsPerSecond']

    original_AggregateCSVfile = filteredJTL_fileDownload_localpath+'Aggregate_report_'+report_number+'X.csv'
    print('Agregate CSV file with path: ', original_AggregateCSVfile)
    
    filtered_AggregateCSVfile = filteredJTL_fileDownload_localpath+'FilteredAggregate_report_'+report_number+'X.csv'
    print('Filtered Agregate CSV file with path: ', filtered_AggregateCSVfile)

    filter_csv_by_strings(original_AggregateCSVfile, filtered_AggregateCSVfile, contentAPI_transactionsList_forReport)

    # Read filtered file to compare with SLAs
    df = pd.read_csv(filtered_AggregateCSVfile)
    loadToDataframe = filter_dataframe(df, sla_avgResponseTime_values)
    filtered_data = add_sla_status(loadToDataframe, sla_avgResponseTime_values, sla_throughput_values, report_number)

    htmlFileName = filteredJTL_fileDownload_localpath+'Summary_'+report_number+'X.html'
    # Create HTML tables
    html_table = filtered_data[['Label', '# Samples', 'Average', 'Median', '90% Line', '95% Line', '99% Line', 'Min', 'Max', 'Error %', 'Throughput', 'Received KB/sec', 'Std. Dev.', 'Response Time SLA Status', 'Throughput SLA Status']].to_html(index=False)
    
    # Modify HTML for collapsible tables and Images
    collapsableSegments = f'''
<script>
function toggleTable(tableId) {{
  var table = document.getElementById(tableId);
  table.style.display = table.style.display === "none" ? "table" : "none";
}}
function toggleImage(imageId) {{
  var imgElement = document.getElementById(imageId);
  if (imgElement.style.display === 'none') {{
      imgElement.style.display = 'block';
  }} else {{
      imgElement.style.display = 'none';
  }}
}}
</script>
'''

    htmlReport_images = f'''
<h2 onclick="toggleImage('graph_atot')">Graph: {image_titles[0]} {report_number}X</h2>
<img id="graph_atot" src="ActiveThreadsOverTime_{report_number}X.png">

<h2 onclick="toggleImage('graph_hps')">Graph: {image_titles[1]} {report_number}X</h2>
<img id="graph_hps" src="HitsPerSecond_{report_number}X.png">

<h2 onclick="toggleImage('graph_rtot')">Graph: {image_titles[2]} {report_number}X</h2>
<img id="graph_rtot" src="ResponseTimesOverTime_{report_number}X.png">

<h2 onclick="toggleImage('graph_tps')">Graph: {image_titles[3]} {report_number}X</h2>
<img id="graph_tps" src="TransactionsPerSecond_{report_number}X.png">
'''
    
    htmlReport_summaryTable = f'''
<h2 onclick="toggleTable('summaryTable')">Aggregate Report {report_number}X</h2>
'''
    
    html_table = html_table.replace('<table', '<table id="summaryTable" style="border-collapse: collapse; display: none;"')

    # Write HTML report to file
    with open(htmlFileName, 'w') as file:
        file.write('<html>\n')
        file.write('<head>\n')
        file.write('<style>\n')
        file.write('table { border-collapse: collapse; }\n')
        file.write('th, td { border: 2px solid rgb(0, 0, 0); padding: 8px; }\n')
        file.write('th { text-align: left; }\n')
        file.write('th {background-color:#85888a; }\n')
        file.write('.red-cell { background-color: rgb(255, 0, 0); }\n')
        file.write('.orange-cell { background-color: rgb(236, 83, 12); }\n')
        file.write('.green-cell { background-color: rgb(0, 128, 0); }\n')
        file.write('body { font-family: Arial, sans-serif; }\n')
        file.write('h1 { font-size: 24px; }\n')
        file.write('h2 { font-size: 18px; cursor: pointer; }\n')
        file.write('</style>\n')
        file.write(collapsableSegments)
        file.write('</head>\n')
        file.write('<body>\n')
        file.write('<h1>Test Report</h1>\n')
        file.write(htmlReport_summaryTable)
        file.write(html_table)

        file.write('\n')
        file.write(htmlReport_images)

        file.write('</body>\n')
        file.write('</html>\n')

    print(f"Filtered data with Response Time SLA status and SampleCount SLA status saved to {htmlFileName}")
