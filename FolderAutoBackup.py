import os
import logging
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
loc = 'Discord Bot'
zip_name = 'SQL Backup '


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

#create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s','%H:%M:%S - %d/%b/%Y')

file_handler = logging.FileHandler('console.log')
file_handler.setFormatter(formatter)

steam_handler = logging.StreamHandler()
steam_handler.setFormatter(formatter)

logger.addHandler(steam_handler)
logger.addHandler(file_handler)


def backup(sched):
        #open lists of zipped file ids
    with open("ids.json", "r") as f:
        ids = json.loads(f.read())
    
    
    #sync json ids to google drive ids
    logger.info("Syncing Zip file ids to Google Drive")   
    gdrive_sync = drive.files().list().execute()
    
    temp = [[],[],[]]
    
    for i in range(len(ids)):
        logger.debug("for loop i running")
        for x in range(len(ids[i])):
            exist = False
            logger.debug("for loop x running")
            for j in range(len(gdrive_sync['files'])):
                logger.debug("for loop j running")
                if ids[i][x] == gdrive_sync['files'][j]['id']:
                    temp[i].insert(0, ids[i][x])
                    logger.debug("THE ONE PIECE IS REAL") 
                else:
                    try:
                        drive.files().delete(fileId = gdrive_sync['files'][j]['id']).execute()
                    except:
                        logger.warning("deleted id that does not exist in google drive")
                    finally:    
                        logger.warning("deleted files that is not registered locally")
    
    ids = list(temp)
    temp = None
                
                    
    logger.info("Done Syncing!")  
    
    
    #converting 2D Array to 1D Array
    hours = ids[0]
    days = ids[1]
    months = ids[2]
    f.close()
    ids = None
    
    
    dt = datetime.datetime.now()
    tstamp = dt.strftime("[%H:%M:%S - %d/%b/%Y] ")
    name = schedule_list[sched]
    fname = zip_name + name + '.zip'
    
    
    #Create Zip
    with zipfile.ZipFile(fname, 'w') as f:
        for file in glob.glob(loc + '/**/*', recursive=True):
            f.write(file)
        f.close()
        
    logger.info("Successfully created an " + name + "Backup")
    
    
    #Upload Zip to Google Drive
    file_metadata = {'name': tstamp + fname}
    media_content = MediaFileUpload(fname)
    
    file = drive.files().create(
        body = file_metadata,
        media_body = media_content
    ).execute()
    
    

    
    
    #adds zipped files id to a list and deleting old ones
    if sched == 0:
        hours.append(file.get('id'))
        while len(hours) > hour:
            drive.files().delete(fileId = hours[0]).execute()
            hours.pop(0)
            logger.warning("one old hourly backup has been deleted")
            
    elif sched == 1:
        days.append(file.get('id'))
        while len(days) > day:
            drive.files().delete(fileId = days[0]).execute()
            days.pop(0)
            logger.warning("one old daily backup has been deleted")
            
    elif sched == 2:
        months.append(file.get('id'))
        while len(months) > month:
            drive.files().delete(fileId = months[0]).execute()
            months.pop(0)
            logger.warning("one old monthly backup has been deleted")
    
    
    #Dumps ids to json file
    f = open("ids.json", "w")
    ids = [hours, days, months]
    f.write(json.dumps(ids))
    f.close()

    
    if file != {}:
        logger.info("Successfully uploaded " + name + "Backup to Google Drive")
        file = {}
    else:
        logger.error("Failed to upload " + name + "Backup to Google Drive")
        
    logger.info("Standby..")   
    


logger.info("I'm Ready to Backup!")

#schedule
#schedule.every().minutes.do(backup, 0)
#schedule.every().day.do(backup, 1)
#schedule.every(30).days.do(backup,2)



while True:
    #cmd = input("input 0 / 1 / 2 for hours / days / months : ")
    #backup(int(cmd))    
    #schedule.run_pending() 
    
    
    
    #python schedule libarary alternative lmao 
    dt = datetime.datetime.now()
    if 282020 > int(dt.strftime("%d%H%M")) > 282000:
        backup(2)
        time.sleep(1200)
    elif 2040 > int(dt.strftime("%H%M")) > 2020:
        backup(1)
        time.sleep(1200)
    else:
        backup(0)
     
        
        
    time.sleep(3600)