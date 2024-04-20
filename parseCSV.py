from pymongo import MongoClient
import datetime
import csv


class
client = MongoClient("localhost", 27017)

db = client.test_database

collection = db.test_collection

col1_data = []
allRows = []

with open("medicalSampleData.csv", newline ='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        col1_data.append(row['SKU ID'])
csvfile.close()

with open("medicalSampleData.csv", newline ='') as csvfile:
    rowReader = csv.reader(csvfile)
    for row in rowReader:
        allRows.append(row)
csvfile.close()

col1_SKU_data = set(col1_data)



# get different transcripts


# create a different file that I can use to create a back and forth response using terminal I think
# and then translate that to the actual transcript



# get a result of the transcript

#figure out how to parse this in order to feedback to the agent
