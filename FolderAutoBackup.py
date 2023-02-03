import os
import numpy as np
import json
import zipfile
import glob
import schedule
import time
import datetime

from googleapiclient.http import MediaFileUpload
from Google import Create_Service


#Folder Location
loc = ''
zip_name = ' '


#Max Stored Zip in Google Drive
hour = 5
day = 10
month = 12


#Google Drive
CLIENT_SECRET_FILE = 'client-secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']



drive = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
schedule_list = ["Hourly ", "Daily ", "Monthly "]

with open("ids.json", "r") as f:
    temp = json.loads(f.read())
hours = temp[0]
days = temp[1]
months = temp[2]
f.close()
temp = None


def backup(sched):
    dt = datetime.datetime.now()
    tstamp = dt.strftime("[%H:%M:%S - %d/%b/%Y] ")
    name = schedule_list[sched]
    fname = zip_name + name + '.zip'
    
    #Create Zip
    with zipfile.ZipFile(fname, 'w') as f:
        for file in glob.glob(loc + '/**/*', recursive=True):
            f.write(file)
        f.close()
        
        
    print(tstamp + "Successfully created a " + name + "Backup")
    
    #Upload Zip to Google Drive
    file_metadata = {'name': tstamp + fname}
    media_content = MediaFileUpload(fname)
    
    file = drive.files().create(
        body = file_metadata,
        media_body = media_content
    ).execute()
    
    
    
    
    if sched == 0:
        hours.append(file.get('id'))
        while len(hours) > hour:
            drive.files().delete(fileId = hours[0]).execute()
            hours.pop(0)
            print("one old hourly backup has been deleted")
            
    elif sched == 1:
        days.append(file.get('id'))
        while len(days) > day:
            drive.files().delete(fileId = days[0]).execute()
            days.pop(0)
            print("one old daily backup has been deleted")
            
    elif sched == 2:
        months.append(file.get('id'))
        while len(months) > month:
            drive.files().delete(fileId = months[0]).execute()
            months.pop(0)
            print("one old monthly backup has been deleted")
    
    
    
    
    f = open("ids.json", "w")
    temp = [hours, days, months]
    f.write(json.dumps(temp))
    f.close()

    
    if file != {}:
        print(tstamp + "Successfully uploaded " + name + "Backup to Google Drive")
        file = {}
    else:
        Print(tstamp + "Failed to upload " + name + "Backup to Google Drive")
        
        
    


print("I'm Ready to Backup!")


schedule.every().hour.do(backup, 0)
schedule.every().day.do(backup, 1)
schedule.every(30).days.do(backup, 2)



while True:
    #cmd = input("input 0 / 1 / 2 for hours / days / months : ")
    #backup(int(cmd))    
    schedule.run_pending()
    time.sleep(1)