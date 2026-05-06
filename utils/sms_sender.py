from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

def send_sms_otp(mobile_number, otp_code):
    try:
        # Initialize Twilio Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send the Message
        message = client.messages.create(
            body=f"Your OTP code is: {otp_code}",
            from_=TWILIO_PHONE_NUMBER,
            to=mobile_number
        )

        # print(f"OTP Sent! SID: {message.sid}")
        
        # RETURN A DICTIONARY (Fixes the 'bool' object error)
        return {"success": True, "message": "SMS sent successfully", "sid": message.sid}

    except Exception as e:
        error_msg = str(e)
        print(f"Twilio Error: {error_msg}")
        
        # RETURN A DICTIONARY (Fixes the 'bool' object error)
        return {f"success": False, "message": error_msg}