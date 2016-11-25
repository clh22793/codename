import csv
from pymongo import MongoClient

collection = "emails"

# INIT DB CONNECTION
def get_mongo_connection():
    conn = MongoClient('mongodb://aws-us-east-1-portal.14.dblayer.com:10871,aws-us-east-1-portal.13.dblayer.com:10856')
    return conn

def db_connection():
    conn = get_mongo_connection()
    conn['betas'].authenticate('devtest', 'devtest', mechanism='SCRAM-SHA-1')
    return conn['betas']

db = db_connection()

emails = db[collection].find()

list = []

for email in emails:
    #print email['email']
    list.append(email['email'])

list = set(list)
print list

print "length: "+str(len(list))

def export_to_csv(filename, list):
    with open(filename, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for item in list:
            spamwriter.writerow([item])
            #spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
            #spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

export_to_csv('output.csv', list)




print "COMPLETED."

