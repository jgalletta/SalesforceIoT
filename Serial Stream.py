# Serial Data Streaming from Arduino to Salesforce
# Created by: Jack Galletta, Summer 2019
# jgalletta@salesforce.com

# import packages
from simple_salesforce import Salesforce, SalesforceLogin
from Credentials import username, password
import serial
import threading
import datetime
import re


# logging into Salesforce
session_id, instance = SalesforceLogin(username=username, password=password)
sf = Salesforce(instance=instance, session_id=session_id)
print('Successfully logged in!')
print('Wating to detect cars...')
# Logged in! Now perform API actions, SOQL queries, etc.

# object to read in serial data from port: '/dev/cu.usbmodem14201'
arduinoData = serial.Serial('/dev/cu.usbmodem14201', 9600)

myid = str(sf.query("SELECT Id FROM Traffic_Tracker__c"))
pattern = "'Id', '(.{18})'"
r1 = re.findall(pattern, myid)
ttid = r1[0]

#query besthour object and strip the ID value
constquery = str(sf.query("SELECT BHID__c FROM BestHourConst__c"))
id = str(sf.query("SELECT Id FROM Best_Hour__c"))
pattern = "'Id', '(.{18})'"
r1 = re.findall(pattern, id)
bhid = r1[0]
if constquery[27] == '0':
    sf.BestHourConst__c.create({"BHID__c": bhid})
    besthourconstupdate = str(sf.query("SELECT BHID__c FROM BestHourConst__c"))
    print("First time setup is complete!")

# creating variables to store data and upload to org
carCount = 0
sensorCount = 0
data = 0
updated = True
totalCars = 0

# opens previously saved car per hour values into array called fullday
fullday = []
with open("hourrecord.txt", 'r') as f:
    for line in f:
        fullday.append(int(line.strip()))

def bestHour():
    threading.Timer(5, bestHour).start()

    currentDT = datetime.datetime.now()

    # determines and assigns best hour fields
    #fullday[int(currentDT.strftime("%H"))] += 1

    #print(fullday)
    currhour = int(currentDT.strftime("%H"))

    # for medium and low priority cases, searches through next 6 hours of traffic data
    medsubset = (fullday[currhour: currhour + 6])

    # for high priority cases, searches through next 3 hours of traffic data
    highsubset = (fullday[currhour: currhour + 3])

    # for critical cases, select the current hour as best time

    medminindex = currhour
    # print(medsubset)
    medmin = medsubset[0]
    for i in range(len(medsubset)):
        if medsubset[i] < medmin:
            medmin = medsubset[i]
            medminindex = currhour + i

    highminindex = currhour
    highmin = highsubset[0]
    for i in range(len(highsubset)):
        if highsubset[i] < highmin:
            highmin = medsubset[i]
            highminindex = currhour + i
            #print(highminindex)

    #print(str(medmin) + ", " + str(medminindex))
    #print(str(highmin) + ", " + str(highminindex))
    sf.Best_Hour__c.update(bhid, {"LowMedium_Priority__c": medminindex, "High_Priority__c": highminindex, "Crit_Priority__c": currhour})

    # saves the array to local file
    with open("hourrecord.txt", "w") as f:
        for i in fullday:
            f.write(str(i) + "\n")


# loop to read data from USB and send to org

def lowerTraffic():
    threading.Timer(15, lowerTraffic).start()
    global carCount, sensorCount
    if carCount > 0:
        carCount -= 1
        sensorCount -= 100
        sf.Traffic_Status__e.create({"Car_Rate__c": carCount, "Sensor_Name__c": "pe test"})
        sf.Traffic_Tracker__c.update(ttid, {"Car_Rate__c": carCount})
        print('Traffic rate lowered to: ' + str(carCount))

#lowerTraffic()
bestHour()

# Initialize platform event record and reset object record
sf.Traffic_Status__e.create({"Car_Rate__c": carCount, "Sensor_Name__c": "pe test"})
sf.Traffic_Tracker__c.update(ttid, {"Car_Rate__c": 0})

while True:
    # reads in serial data, strips it, and decodes it
    rawdata = (arduinoData.readline().strip())
    data = int(rawdata.decode('utf-8'))
    # extra print statement for viewing live da ta/debugging
    #print(data)

    # checks to see if object is <= 10cm from sensor and in front of sensor for > 1s
    if data <= 10:
        sensorCount += 1
        if sensorCount %80 == 0:
            carCount = int(sensorCount/80);
            print('Car detected, cars counted is: ' + str(carCount))
            totalCars += 1

            #   ~~~THE MAGIC LINE OF CODE~~~
            # upserts a platform event of type traffic_status__e into the org, using # of cars counted as a parameter
            sf.Traffic_Status__e.create({"Car_Rate__c": carCount, "Sensor_Name__c": "pe test"})
            sf.Traffic_Tracker__c.update(ttid, {"Car_Rate__c": carCount})
            #   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            print('Platform Event and Object successfully upserted')
            currentDT = datetime.datetime.now()
            sf.Car__c.create({"Name": 'c' + str(totalCars), "Location__c": 'Reston', "Hour__c": currentDT.strftime("%H"), "Timestamp__c": currentDT.strftime("%H:%M:%S")})
            #print('Car timestamp record successfully created')

            #increments cars within the hour
            fullday[int(currentDT.strftime("%H"))] += 1