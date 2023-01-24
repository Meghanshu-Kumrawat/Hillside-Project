from datetime import datetime
import pyotp
import base64
from django.conf import settings
import requests
from twilio.rest import Client

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
class SendSMS:
    def __init__(self, phone, message):
        # Your Account Sid and Auth Token from twilio.com/console
        self.account_sid = 'AC49a7a3f6b96a04ed8ce280ca2ce771a6'
        self.auth_token = 'd257d62ccee8eaec06692a2bea04346a'
        client = Client(self.account_sid, self.auth_token)

        message = client.messages.create(
            body=message,
            from_='+12565679977',
            to="+91" + phone
        )

        print(message.sid)
