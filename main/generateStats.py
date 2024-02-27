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

rawJTL_fileDownload_localpath = 'C:/Users/VRATNSI/Downloads/ContentAPI_30thJune2023_ReleaseV2/'
jmeter_path = 'C:\\Users\\VRATNSI\\Downloads\\apache-jmeter-5.5\\apache-jmeter-5.5\\bin\\'
filteredJTL_fileDownload_localpath_win = rawJTL_fileDownload_localpath
fullRawJTL_fileName = 'ContentAPI_30thJune2023_ReleaseV2.jtl'
file_name = fullRawJTL_fileName
report_number = '0'

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

generate_individualStats(filteredJTL_fileDownload_localpath_win, file_name, report_number)
