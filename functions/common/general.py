import os
import json
import datetime, time

config_path = os.path.join(os.path.dirname(__file__), '..','..', 'log_config', 'log_setting.config')
print("Current config path: "+config_path)

#--------------------------------------------------------------------
# Time stamp functions
#--------------------------------------------------------------------
def get_formatted_current_time():
    current_time = datetime.datetime.now()
    formatted_time = "\n"+current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+" "
    return formatted_time

def get_formatted_current_time_for_fileName():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y%m%dT%H%M%S')
    return formatted_time
#--------------------------------------------------------------------


#--------------------------------------------------------------------
#Logging Function
#--------------------------------------------------------------------
def logInitialMessage(message, logFileName):
    with open(logFileName, 'a') as log_file:
        current_time = datetime.datetime.now()
        log_file.write(current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+" "+str(message).replace('\n','; '))
#--------------------------------------------------------------------
def logging(message, logFileName):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        logging_enabled = config.get("LOGGING_ENABLED")
        consolelogging_enabled = config.get("CONSOLE_LOGGING_ENABLED")
        logfile_enabled = config.get("LOGFILE_ENABLED")    
    if logging_enabled == 1:
        if consolelogging_enabled == 1:
            print(message)
        if logfile_enabled == 1:
            with open(logFileName, 'a') as log_file:
                log_file.write(get_formatted_current_time()+str(message).replace('\n','; '))
#--------------------------------------------------------------------
def loggingwoTimestamp(message, logFileName):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        logging_enabled = config.get("LOGGING_ENABLED")
        consolelogging_enabled = config.get("CONSOLE_LOGGING_ENABLED")
        logfile_enabled = config.get("LOGFILE_ENABLED")    
    if logging_enabled == 1:
        if consolelogging_enabled == 1:
            print(message)
        if logfile_enabled == 1:
            with open(logFileName, 'a') as log_file:
                log_file.write("\n"+" "*24+str(message).replace('\n','; '))                
#--------------------------------------------------------------------
def loggingSectionName(message, logFileName):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        logging_enabled = config.get("LOGGING_ENABLED")
        consolelogging_enabled = config.get("CONSOLE_LOGGING_ENABLED")
        logfile_enabled = config.get("LOGFILE_ENABLED")    
    if logging_enabled == 1:
        if consolelogging_enabled == 1:
            print(message)
        if logfile_enabled == 1:
            with open(logFileName, 'a') as log_file:
                log_file.write("\n"+" "*24+"-"*40)
                log_file.write(get_formatted_current_time()+str(message).replace('\n','; '))
                log_file.write("\n"+" "*24+"-"*40)
#--------------------------------------------------------------------


#--------------------------------------------------------------------
#Wait Time  Function
#--------------------------------------------------------------------
def wait(waitTime, logFileName):
    if int(waitTime) >= 1:
        logging('Waiting for '+waitTime+' Seconds.',logFileName)
        time.sleep(int(waitTime))
#--------------------------------------------------------------------
