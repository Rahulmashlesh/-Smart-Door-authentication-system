import json
import boto3
dynamodbClient = boto3.client('dynamodb')
print('Loading function')


def lambda_handler(event, context):
    #TODO : go check if event["passcode"] exist in DynamoDB
    passcode = event["passcode"]
    #print(passcode)
    passcode_db_response = dynamodbClient.get_item(
        TableName='Passcodes',
        Key = {
            "passcode": {
                "S": passcode
            }
        }
        )
    passcode_item = passcode_db_response.get("Item")
    response = {
        "exisitence": "0"
    }
    if (passcode_item is not None) :
        response["exisitence"] = "1"
        faceID = passcode_item["faceID"]["S"]
        #print("passcode " + passcode + " will get faceID:" + faceID)
        visitor_db_response = dynamodbClient.get_item(
            TableName='visitors',
            Key = {
                "faceId": {
                    "S": faceID
                }
            }
        )
        print(visitor_db_response)
        # visitor_item won't be None
        visitor_item = visitor_db_response.get("Item")
        print(visitor_item)
        visitor_data = json.loads(visitor_item["data"]['S'])
        
        visitor_name = visitor_data["name"]
        response["name"] = visitor_name
        
        #print(visitor_db_response)
        
    return json.dumps(response)
