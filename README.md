# Smart Door authentication system

Implemented a Smart Door authentication system.
Used Kinesis Video Streams and Amazon Rekognition to build a distributed system that authenticates people and provides them with access to a virtual door.

![image](https://user-images.githubusercontent.com/8120359/183783497-d5e01d55-dcb2-4c95-a890-fddd06e09b7e.png)


### Visitor Vault:
a. Created a S3 bucket (B1) to store the photos of the visitors.
b. Created a DynamoDB table “passcodes” (DB1) that stores temporary access codes to your virtual door and a reference to the visitor it was assigned to. Used the TTL feature of DynamoDB to expire the records after 5 minutes.
c. Created a DynamoDB table “visitors” (DB2) that stores details about the visitors that your Smart Door system is interacting with. Indexed each visitor by the FaceId detected by Amazon Rekognition2 (more in the next section), alongside the name of the visitor and their phone number. When storing a new face, if the FaceId
returned by Rekognition already exists in the database, appended the new photo to the existing photos array.

### Video Analysis and image processing:
a. Created a Kinesis Video Stream (KVS1), that will be used to capture and 3 stream video for analysis. You can use the built-in video recording feature in the Kinesis console to simulate a real streaming video camera.
b. Subscribe Rekognition Video to the Kinesis Video Stream (KVS1). 4
c. Output the Rekognition Video analysis to a Kinesis Data Stream (KDS1) and trigger a Lambda function (LF1) for every event that Rekognition Video outputs.
d. For every known face detected by Rekognition, send the visitor an SMS 5 message to the phone number on file. The text message should include a PIN or a One-Time Passcode (OTP) that they can use to open the virtual door. Store the OTP in the “passcodes” table (DB1), with a 5 minute expiration timestamp.
e. For every unknown face detected by Rekogniton, send an SMS to the “owner” (i.e. yourself or a team member) a photo of the visitor. The text message should also include a link to approve access for the visitor.
i. If clicked, the link should take you to a simple web page (WP1) that collects the name and phone number of the visitor via a web form. Submitting this form will  create a new record in the “visitors” table (DB2), indexed by the FaceId identified by Rekognition.

### Authorize
Creates a second web page (WP2), the “virtual door”, that prompts the user to input the OTP. If the OTP is valid, greet the user by name and present a success
message, If the OTP is invalid,  a “permission denied” message will be displayed. 
