from pathlib import Path
from random import randint
from twilio.rest import Client
from django.conf import settings

# account_sid = env('TWILLIOSID', default='')
# auth_token = env('TWILLIOAUTHTOKEN', default='')
# client = Client(account_sid, auth_token)

client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
def generate_otp()->str:
    """
    Generate a 6-digit OTP.
    """
    otp = str("1111")
    return otp


def send_otp_via_sms(phone_number: str, otp: str) -> bool:
    """
    Send OTP to the user's phone number via SMS.
    """
    # Placeholder for actual SMS sending logic
    print(f"Sending OTP {otp} to {phone_number}")
    message = client.messages.create(
        from_='+19342390741',
        body=f'Your OTP is {otp}',
        to=f'{phone_number}'
    )
    print("OTP Sent")
    print(message.sid)
    return True
    # In a real application, you would integrate with an SMS gateway API here.
    
    
    

    
    
if __name__ == "__main__":
    pass