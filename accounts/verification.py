from datetime import datetime
import pyotp
import base64
from django.conf import settings
import requests

class GenerateOTP:

    def returnValue(self, token):
        return str(token) + str(datetime.date(datetime.now())) + "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"

    def gererate(self, token):
        key = base64.b32encode(self.returnValue(token).encode())
        OTP = pyotp.TOTP(key,interval = settings.EXPIRY_TIME)
        return OTP

    def verify(self, token, otp):
        key = base64.b32encode(self.returnValue(token).encode())  # Generating Key
        OTP = pyotp.TOTP(key,interval = settings.EXPIRY_TIME)  # TOTP Model 
        return OTP.verify(otp)  # Verifying the OTP


# function for sending SMS
def sendSMS(message, phone):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": "9nB0DrAd1mqZI8vcJFLg3ouMbjkGEYpRi7aXwhW2Q6f54CzPeUo7bwdsYp3k6Sx4J8EgPl9KIvNnt2jr",
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": phone}

    headers = {
        'cache-control': "no-cache"
    }
    try:
        response = requests.request("GET", url,
                                    headers = headers,
                                    params = querystring)
        
        print("SMS Successfully Sent")
        return True
    except:
        print("Oops! Something wrong")
        return False