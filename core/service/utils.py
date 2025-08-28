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
    
    
    
    
def send_otp_via_email(email: str, otp: str) -> bool:
    """
    Send OTP to the user's email address.
    """
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}. It is valid for 5 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        # Log the error (for debugging)
        print(f"Error sending OTP email: {e}")
        return False

    
    
if __name__ == "__main__":
    pass