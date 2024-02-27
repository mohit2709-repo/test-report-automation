
import os
import datetime
from datetime import datetime

import pandas as pd
import datetime as dt


print("Running")
#os.system("aws ec2 describe-instances --query \"Reservations[*].Instances[*].{Launch_Time:LaunchTime,Owner_Name:Tags[?Key==\'t_owner_individual\']|[0].Value,Application_Name:Tags[?Key==\'customer\']|[0].Value,PublicIP:PublicIpAddress,Type:InstanceType,Name:Tags[?Key==\'Name\']|[0].Value,Status:State.Name}\" --filters \"Name=instance-state-name,Values=running\" \"Name=tag:Name,Values=\'*\'\" --output json > D:\Automation_Test_Results\Test_Case\Running_%date%.json")
os.system("aws-runas Prod aws ec2 describe-instances --query \"Reservations[*].Instances[*].{Launch_Time:LaunchTime,Owner_Name:Tags[?Key==\'t_owner_individual\']|[0].Value,Application_Name:Tags[?Key==\'customer\']|[0].Value,PublicIP:PublicIpAddress,Type:InstanceType,Name:Tags[?Key==\'Name\']|[0].Value,Status:State.Name}\" --filters \"Name=instance-state-name,Values=running\" \"Name=tag:Name,Values=\'*\'\" --output json > D:\Automation_Test_Results\Test_Case\Running_%date%.json")
print("Stopped")
#os.system("aws ec2 describe-instances --query \"Reservations[*].Instances[*].{Launch_Time:LaunchTime,Owner_Name:Tags[?Key==\'t_owner_individual\']|[0].Value,Application_Name:Tags[?Key==\'customer\']|[0].Value,PublicIP:PublicIpAddress,Type:InstanceType,Name:Tags[?Key==\'Name\']|[0].Value,Status:State.Name}\" --filters \"Name=instance-state-name,Values=stopped\" \"Name=tag:Name,Values=\'*\'\" --output json > D:\Automation_Test_Results\Test_Case\Stopped_%date%.json")
os.system("aws-runas Prod aws ec2 describe-instances --query \"Reservations[*].Instances[*].{Launch_Time:LaunchTime,Owner_Name:Tags[?Key==\'t_owner_individual\']|[0].Value,Application_Name:Tags[?Key==\'customer\']|[0].Value,PublicIP:PublicIpAddress,Type:InstanceType,Name:Tags[?Key==\'Name\']|[0].Value,Status:State.Name}\" --filters \"Name=instance-state-name,Values=stopped\" \"Name=tag:Name,Values=\'*\'\" --output json > D:\Automation_Test_Results\Test_Case\Stopped_%date%.json")

now = datetime.now()

print("now =", now)
dt_string = now.strftime("%d-%m-%Y")

print (dt_string)
c1 = "Running_" + dt_string
c = "Running_" + dt_string + ".json"
print(c1)
#os.system("aws ec2 describe-instances --query \"Reservations[*].Instances[*].{Launch_Time:LaunchTime,Owner_Name:Tags[?Key==\'t_owner_individual\']|[0].Value,Application_Name:Tags[?Key==\'customer\']|[0].Value,PublicIP:PublicIpAddress,Type:InstanceType,Name:Tags[?Key==\'Name\']|[0].Value,Status:State.Name}\" --filters \"Name=instance-state-name,Values=stopped\" \"Name=tag:Name,Values=\'*\'\" --output table")

#aws ec2 describe-instances --query "Reservations[*].Instances[*].{Launch_Time:LaunchTime,Owner_Name:Tags[?Key=='t_owner_individual']|[0].Value,Application_Name:Tags[?Key=='customer']|[0].Value,PublicIP:PublicIpAddress,Type:InstanceType,Name:Tags[?Key=='Name']|[0].Value,Status:State.Name}" --filters "Name=instance-state-name,Values=stopped" "Name=tag:Name,Values='*'" --output table





File_Name = "D:\Automation_Test_Results\Test_Case" + "\\" + c
print(File_Name)


#input file Remove [ ] and 00:00+
fin = open(File_Name, "rt")
fout = open(File_Name+"_1", "wt")

for line in fin:
    fout.write(line.replace('[', ''))

fin.close()
fout.close()

fin = open(File_Name+"_1", "rt")
fout = open(File_Name+"_2", "wt")

for line in fin:
    fout.write(line.replace(']', ''))

fin.close()
fout.close()

"""
fin = open(File_Name+"_2", "rt")
fout = open(File_Name+"_3", "wt")

for line in fin:
    fout.write(line.replace('+00:00', ''))

fin.close()
fout.close()

"""

d = "Running_" + dt_string + "Edit.json"
print(d)

# Add [] to the file
sample = open(File_Name+"_3", 'w')

print('[', file=sample)
sample.close()


with open(File_Name+"_2", 'r') as firstfile, open(File_Name+"_3", 'a') as secondfile:
    # read content from first file
    for line in firstfile:
        # append content to second file
        secondfile.write(line)

sample.close()

sample = open(File_Name+"_3", 'a')

print(']', file=sample)
sample.close()

e= File_Name + "_3"

print(e)

Test_File_csv = "D:\Automation_Test_Results\Test_Case" + "\\" + c1

#final Print Values in the csv
df = pd.read_json(e)
df.to_csv(Test_File_csv+".csv")

Final_csv= Test_File_csv+".csv"

print(Final_csv)


text = open(Final_csv, "r")

# join() method combines all contents of
# csvfile.csv and formed as a string
text = ''.join([i for i in text])

# search and replace the contents
text = text.replace("+00:00", "")


# output.csv is the output file opened in write mode
x = open(Test_File_csv+"train.csv", "w")

# all the replaced text is written in the output.csv file
x.writelines(text)
x.close()

Final_csv1= Test_File_csv+"train.csv"
print(Final_csv1)

#Difference of Current Data and Lauch Time, Calculations of hrs and days.

import pandas as pd
from datetime import datetime
import datetime as dt

df = pd.read_csv(Final_csv1)


#df['Launch_Time'] = pd.to_datetime(df['Launch_Time'], format="%D-%M-%Y %H:%M:%S")
df['Launch_Time'] = pd.to_datetime(df['Launch_Time'], format="mixed")
#df['Now'] = pd.to_datetime(df['Now'], format="%d-%m-%Y %H:%M")

now = datetime.now()

print("now =", now)
dt_string = now.strftime("%d-%m-%y %H:%M")
print(dt_string)

#df['handling_time'] = df['Now'] - df['Launch_Time']

#df.to_csv('D:\Automation_Test_Results\TT_Check_1.csv', index=False)

df['Running_days'] = (dt.datetime.now() - df['Launch_Time']).dt.days
df['Running_hrs'] = (dt.datetime.now() - df['Launch_Time']).dt.components['hours']


df.sort_values(df.columns[8],axis=0, inplace= True)
#print(dataFrame)
#df = pd.read_csv('D:\File1.csv', usecols=cols)
df.to_csv(Test_File_csv+"_Final.csv", index=False)
#dataFrame.to_csv('D:\Office_Automation\Jmeter_Interim_Results\CSG\Final2x.csv', index=False)


#os.remove(c1+".csv")
os.remove(File_Name)
os.remove(File_Name+"_1")
os.remove(File_Name+"_2")
os.remove(File_Name+"_3")
os.remove(Final_csv)
os.remove(Final_csv1)



#--------Stopped-----------------
#now = datetime.now()

#print("now =", now)
dt_string = now.strftime("%d-%m-%Y")

#print (dt_string)
s1 = "Stopped_" + dt_string
s = "Stopped_" + dt_string + ".json"
print(s1)


sFile_Name = "D:\Automation_Test_Results\Test_Case" + "\\" + s
print(sFile_Name)


#input file Remove [ ] and 00:00+
fin = open(sFile_Name, "rt")
fout = open(sFile_Name+"_1", "wt")

for line in fin:
    fout.write(line.replace('[', ''))

fin.close()
fout.close()

fin = open(sFile_Name+"_1", "rt")
fout = open(sFile_Name+"_2", "wt")

for line in fin:
    fout.write(line.replace(']', ''))

fin.close()
fout.close()

"""
fin = open(File_Name+"_2", "rt")
fout = open(File_Name+"_3", "wt")

for line in fin:
    fout.write(line.replace('+00:00', ''))

fin.close()
fout.close()

"""

d = "Running_" + dt_string + "Edit.json"
print(d)

# Add [] to the file
sample = open(sFile_Name+"_3", 'w')

print('[', file=sample)
sample.close()


with open(sFile_Name+"_2", 'r') as firstfile, open(sFile_Name+"_3", 'a') as secondfile:
    # read content from first file
    for line in firstfile:
        # append content to second file
        secondfile.write(line)

sample.close()

sample = open(sFile_Name+"_3", 'a')

print(']', file=sample)
sample.close()

e= sFile_Name + "_3"

print(e)

sTest_File_csv = "D:\Automation_Test_Results\Test_Case" + "\\" + s1

#final Print Values in the csv
df = pd.read_json(e)
df.to_csv(sTest_File_csv+".csv")

sFinal_csv= sTest_File_csv+".csv"

print(sFinal_csv)


text = open(sFinal_csv, "r")

# join() method combines all contents of
# csvfile.csv and formed as a string
text = ''.join([i for i in text])

# search and replace the contents
text = text.replace("+00:00", "")


# output.csv is the output file opened in write mode
x = open(sTest_File_csv+"train.csv", "w")

# all the replaced text is written in the output.csv file
x.writelines(text)
x.close()

sFinal_csv1= sTest_File_csv+"train.csv"
print(sFinal_csv1)

#Difference of Current Data and Lauch Time, Calculations of hrs and days.

import pandas as pd
from datetime import datetime
import datetime as dt

df = pd.read_csv(sFinal_csv1)


#df['Launch_Time'] = pd.to_datetime(df['Launch_Time'], format="%D-%M-%Y %H:%M:%S")
df['Launch_Time'] = pd.to_datetime(df['Launch_Time'], format="mixed")
#df['Now'] = pd.to_datetime(df['Now'], format="%d-%m-%Y %H:%M")

now = datetime.now()

print("now =", now)
dt_string = now.strftime("%d-%m-%y %H:%M")
print(dt_string)

#df['handling_time'] = df['Now'] - df['Launch_Time']

#df.to_csv('D:\Automation_Test_Results\TT_Check_1.csv', index=False)

df['Running_days'] = (dt.datetime.now() - df['Launch_Time']).dt.days
df['Running_hrs'] = (dt.datetime.now() - df['Launch_Time']).dt.components['hours']


df.sort_values(df.columns[8],axis=0, inplace= True)
#print(dataFrame)
#df = pd.read_csv('D:\File1.csv', usecols=cols)
df.to_csv(sTest_File_csv+"_Final.csv", index=False)
#dataFrame.to_csv('D:\Office_Automation\Jmeter_Interim_Results\CSG\Final2x.csv', index=False)


#os.remove(c1+".csv")
os.remove(sFile_Name)
os.remove(sFile_Name+"_1")
os.remove(sFile_Name+"_2")
os.remove(sFile_Name+"_3")
os.remove(sFinal_csv)
os.remove(sFinal_csv1)




