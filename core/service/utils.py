from random import randint

from twilio.rest import Client
account_sid = 'AC76baa4cbac29f39750dba75bd09971a8'
auth_token = 'f3115f991dbb9d34151fd59cc503d141'
client = Client(account_sid, auth_token)

def generate_otp()->str:
    """
    Generate a 6-digit OTP.
    """
    otp = str(randint(1000, 9999))
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