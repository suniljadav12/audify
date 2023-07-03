import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Path to the Firebase service account key JSON file
service_account_path = "C:/Users/jadav/Downloads/video-to-audio-71cb2-firebase-adminsdk-td7pc-cb96ba1326.json"



# Initialize Firebase
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred, {'storageBucket': "video-to-audio-71cb2.appspot.com"})

# Get a reference to the default Firebase Storage bucket
bucket = storage.bucket()

