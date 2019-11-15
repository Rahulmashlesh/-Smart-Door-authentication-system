import json
import boto3
import base64
import uuid
import botocore.vendored.requests as requests
import time
import random
import cv2

video_client = boto3.client('kinesis-video-media',endpoint_url='https://s-1e415f8b.kinesisvideo.us-east-1.amazonaws.com',region_name='us-east-1')
kinesis_client = boto3.client('kinesisvideo',region_name='us-east-1')
rekognition_client=boto3.client('rekognition')
dynamodbClient = boto3.client('dynamodb')
sns_client = boto3.client('sns')
s3 = boto3.client('s3')

owner_phone_number = "+19293104679"

def lambda_handler(event, context):
    print("START SMART DOOR CYCLE LF1")
    #getURL()
    extract_frame(event)
    print("End of main funciton.")
    return {
        'statusCode' : 200,
        'body': json.dumps('Hello from Lambda!')
    }

def extract_frame(event):
    print("Extracting Frames")
    record = event['Records'][0]
    payload=base64.b64decode(record["kinesis"]["data"])
    print('Decoded payload:', payload)
    faceinfo = json.loads(payload.decode('utf-8'))
    faces = faceinfo["FaceSearchResponse"]
    faceId = ''
    check_frame = False
    face_raw_image='pi_Video_'
    for f in faces:
        print('Face Found')
        for matchedFace in f["MatchedFaces"]:
            mf = matchedFace["Face"]
            faceId = mf["FaceId"]
            print("Got FaceID:" + faceId)
        if 'InputInformation' in faceinfo:
            x = faceinfo["InputInformation"]
            y = x["KinesisVideo"]
            fn = y["FragmentNumber"]
            print("Print triplet")
            print(x,y,fn)
            stream = video_client.get_media(
                StreamARN='arn:aws:kinesisvideo:us-east-1:044197594723:stream/PiStream/1573482770601',
                StartSelector={
                    'StartSelectorType': 'FRAGMENT_NUMBER',
                    'AfterFragmentNumber': fn
                }
            )
            
            with open('/tmp/stream.mkv', 'wb') as f:
                streamBody = stream['Payload'].read(480*640)
                f.write(streamBody)
                vcap = cv2.VideoCapture('/tmp/stream.mkv')
                ret, frame = vcap.read()
                if frame is not None:
                    # Display the resulting frame
                    vcap.set(1, int(vcap.get(cv2.CAP_PROP_FRAME_COUNT)/2)-1)
                    face_raw_image=face_raw_image+time.strftime("%Y%m%d-%H%M%S")+'.jpg'
                    cv2.imwrite('/tmp/'+face_raw_image,frame)
                    s3.upload_file('/tmp/'+face_raw_image, 'hw2-faces', face_raw_image)
                    vcap.release()
                    print('Image uploaded to S3 :', face_raw_image)
                    check_frame = True
                    break
                else:
                    print("Frame is None")
                    break
        break

    if check_frame or faceId:
        print("Stage0: Frame or Face detected")
        if faceId != '': 
            # Recognized Face found
            face_analyzer(faceId, face_raw_image)
        else:
            # Unknown face, send it to rekognition to generate a faceID
            print("Unknown Face Detected, Starting the Training Process")
            #time.sleep(3)
            rekognition_train_response=rekognition_client.index_faces(CollectionId='newfaces',
                                        Image={'S3Object':{'Bucket':'hw2-faces','Name':face_raw_image}},
                                        ExternalImageId=face_raw_image,
                                        MaxFaces=1,
                                        QualityFilter="AUTO",
                                        DetectionAttributes=['ALL'])
            
            print("Reckognition response: ")
            print(rekognition_train_response)
            pass


def get_test_faceID(event):
    test_data_faceID = "5cc082a5-e928-4c2c-86a6-f8d43f894765qq"
    test_data_finalKey = "kvs1_20191115-220618.jpg"
    return test_data_faceID, test_data_finalKey

def face_analyzer(faceID, objectKey):
    print("Analyzing facial data")
    
    if (check_has_a_valid_OPT(faceID)):
        # CASE 1: Visitor has a vaild OTP
        # Do nothing
        return
    
    elif (check_if_Known_Visitor(faceID)):
        # CASE 2: Visitor is a return known Visitor
        # He/She needs a needs a new OTP
        print("Generating new password for known Visitor")
        new_otp = get_random_otp()

        # Update Passcode DB with new OTP and get visitor Phone number
        visitor_phoneNumber =  insert_DB_OTP_in_passcode(faceID, new_otp)

        # Send SMS to Known Visitor
        response_sns_text = 'Welcome. Your new OTP code is : ' + new_otp + ". To access, click : https://mysmartdoor.s3-us-west-2.amazonaws.com/webpage-1/index.html"
        send_sms(visitor_phoneNumber, response_sns_text)
        print("sent a SMS to visitor : " + visitor_phoneNumber + " with the OTP : " + new_otp)
        return
    
    else:
        # CASE 3: Visitor is new, need to notify the owner
        print("New Visitor detected, New faceID found")

        # Prevent D-DOS on Owner        
        if (owner_flood_prevent(faceID)):
            # If sms with OTP was sent during the last two minutes. 
            # Do nothing
            return
        else:
            # Need to send or re-send a SMS to owner
            owner_page_prefix = "https://mysmartdoor.s3-us-west-2.amazonaws.com/webpage-2/index.html" + "?faceID=" + faceID + "&objectKey=" + objectKey
            response_sns_text = 'A new visitor request! To approve it, click: ' + owner_page_prefix

            # Send SMS to owner
            send_sms(owner_phone_number, response_sns_text)
            print("SMS sent to owner Mobile: " + owner_phone_number + " SMS data: " + response_sns_text)

            # Update DB 
            insert_DB_Face_On_Door_Step(faceID)
    return 

def check_has_a_valid_OPT(faceID):
    #return True if, faceId has a valid OTP in the Passcodes DB
    visitor_scan_response = dynamodbClient.scan(TableName="Passcodes")
    print(visitor_scan_response)
    if (len(visitor_scan_response['Items']) != 0):
        for item in visitor_scan_response['Items']:
            if(faceID == item['faceID']['S']):
                passcode = item['passcode']['S']
                ttl = item['ttl']['N']
                if (time.time() < int(ttl)):
                    #if the item is still valid
                    print("Visitor has a active OTP : " + passcode)
                    return True
                print("Visitor OTP has Expired")
                return False
    else:
        #Passcodes db is empty
        print("Passcode DB is empty, no visitors OTP found")
        return False
    return False

def check_if_Known_Visitor(faceID):
    # Return True if, Visitor in known, i.e faceID is found in Visitor DB
    visitor_response = dynamodbClient.get_item(
        TableName="visitors",
        Key= {
            'faceId': {
                'S': faceID
            }
        }
    )
    if (visitor_response.get('Item') is not None):
        print("Known visitor found, faceID: " + faceID)

        return True
    else:
        return False

def insert_DB_Face_On_Door_Step(faceID):   
    dynamodbClient.put_item(
        TableName="faceOnDoorStep",
        Item = {
            'faceID': {
                'S': faceID
            },
            'ttl': {
                'N': str(int(time.time() + 120))
            }
        }
    )

def insert_DB_OTP_in_passcode(faceID, new_otp):
    visitor_response = dynamodbClient.get_item(
        TableName="visitors",
        Key= {
            'faceId': {
                'S': faceID
            }
        }
    )
    visitor_data = json.loads(visitor_response['Item']['data']['S'])
    visitor_phoneNumber = visitor_data['phoneNumber']
    dynamodbClient.put_item(
        TableName="Passcodes",
        Item = {
            'faceID': {
                'S': faceID
            },
            'passcode':{
                'S': new_otp
            },
            'ttl': {
                'N': str(int(time.time() + 300))
            }
        }
    )
    return visitor_phoneNumber

def send_sms(phone_number,response_sns_text):
    sns_client.publish(
        PhoneNumber = phone_number,
        Message = response_sns_text,
        MessageStructure='string',
    )
    print("SMS sent")

def owner_flood_prevent(faceID):
    # Return true if a sms was sent in the last two minutes.
    pre_check_response = dynamodbClient.get_item(
        TableName="faceOnDoorStep",
        Key= {
            'faceID': {
                'S': faceID
            }
        })
    if (pre_check_response.get("Item") is not None):
        timestamp_for_last_sms = pre_check_response['Item']['ttl']['N']
        if (time.time() < int(timestamp_for_last_sms)):
            print("Found a sms to owner: wait for 2 minutes")
            return True
        else:
            return False

def get_random_otp():
    passcode = ''
    while True:
        otp = 0
        for _ in range(1,5):
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
            print("New OPT: " + passcode)
            break
        else:
            print("Oops!! cretaed new OTP but found duplicate: " + passcode + " Lets Generate a new one")
            get_random_otp()
    return passcode
    
def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def getURL():
    response = kinesis_client.get_data_endpoint(StreamARN='arn:aws:kinesisvideo:us-east-1:044197594723:stream/PiStream/1573482770601',APIName='GET_MEDIA')
    print(response)

