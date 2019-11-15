import json
import boto3
import time
import random
from datetime import datetime
dynamodbClient = boto3.client('dynamodb')
print('Loading function')

def get_random_otp():
    print("getting a new otp")
    passcode = ''
    while True:
        otp = 0
        for i in range(1,5):
            otp += random.randint(0,9)
            otp*=10
        passcode = str(otp)
        passcode_response = dynamodbClient.get_item(
            TableName="Passcodes",
            Key = {
                "passcode": {
                    'S': passcode
                }
            }
        )
        if (passcode_response.get("Item") is None):
            #it is unique
            break;
        else:
            print(passcode + " exists")
    return passcode
    
def lambda_handler(event, context):
    #it is sure that passcode passed in is unique.
    
    passcode = get_random_otp()
    #if this passcode already exists, do it again
    print(passcode)
    
    
    
    name = event["name"]
    objectKey = event["objectKey"]
    phoneNumber = event["phoneNumber"]
    faceID = event["faceID"]
    
    

    #TODO : put a new item into dynamoDB visitor
    #need a faceID 
    response = dynamodbClient.get_item(
        TableName="visitors",
        Key = {
            "faceId": {
                'S': faceID
            }
        }
        )
    
    if (response.get("Item") is None):
        #this is an unknown face
        
        data = {
        "faceID":faceID,
        "name": name,
        "phoneNumber": phoneNumber,
        "photos": [
                {
                    "objectKey": objectKey,
                    "bucket": "mysmartdoor",
                    "createdTimestamp": str(datetime.now())
                }
                ]
        }
        
        jdata = json.dumps(data)
        print("putting item into visitors")
        timestamp = str(datetime.now())
        dynamodbClient.put_item(
            TableName="visitors",
            Item = {
                'faceId': {
                    'S': faceID
                },
                'data': {
                    'S': jdata
                }
            }
            )
    else:
        #this is a known face
        visitor_item = response.get("Item")
        data_dict = json.loads(visitor_item['data']['S'])
        data_dict['photos'].append(
            {
                'objectKey': objectKey,
                'bucket': "mysmartdoor",
                'createdTimestamp': str(datetime.now())
            }
            )
        data_dict['name'] = name
        data_dict['phoneNumber'] = phoneNumber 
        
        jdata = json.dumps(data_dict)
        
        dynamodbClient.put_item(
            TableName="visitors",
            Item = {
                'faceId': {
                    'S': faceID
                },
                'data': {
                    'S': jdata
                }
            }
            )
        
    #TODO : put a new item into dynamoDB passcodes
    dynamodbClient.put_item(
            TableName="Passcodes",
            Item = {
                'faceID': {
                    'S': faceID
                },
                'passcode': {
                    'S': passcode
                },
                'ttl': {
                    'N': str(int(time.time() + 300))
                }
            }
            )
    sns_client = boto3.client('sns')
    response_sns_text = "Welcome " + name + ". Your OTP code is : " + passcode + ". To access, click : https://mysmartdoor.s3-us-west-2.amazonaws.com/webpage-1/index.html"
    sns_client.publish(
        PhoneNumber = phoneNumber,
        Message = response_sns_text,
        MessageStructure='string',
    )
    return event
