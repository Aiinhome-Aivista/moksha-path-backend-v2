
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from config import SENDGRID_API_KEY, FROM_EMAIL

# def send_otp_email(to_email, otp_code):
#     """
#     Sends OTP using Twilio SendGrid Email API.
#     """
#     try:
#         subject = "Your Login Verification Code"
#         html_content = f"""
#         <div style="font-family: Arial, sans-serif; padding: 20px;">
#             <h2>Login Verification</h2>
#             <p>Your One-Time Password (OTP) is:</p>
#             <h1 style="color: #2c3e50; letter-spacing: 5px;">{otp_code}</h1>
#             <p>Valid for 10 minutes.</p>
#         </div>
#         """

#         message = Mail(
#             from_email=FROM_EMAIL,
#             to_emails=to_email,
#             subject=subject,
#             html_content=html_content
#         )

#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)

#         if 200 <= response.status_code < 300:
#             print(f"✅ SendGrid Email Sent to {to_email}")
#             return True
#         else:
#             print(f" SendGrid Failed. Status: {response.status_code}")
#             return False

#     except Exception as e:
#         print(f" Error sending Email via SendGrid: {str(e)}")
#         return False

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, FROM_EMAIL

def send_otp_email(to_email, otp_code):
    """
    Sends a professional HTML OTP email using Twilio SendGrid.
    """
    try:
        # Professional Subject Line
        subject = "Verify your login"
        
        # Professional HTML Template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login Verification</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f7;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; margin-top: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                
                <tr>
                    <td align="center" style="padding: 30px 20px; background-color: #2c3e50;">
                        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px;">
                            Moksha Path Education
                    </td>
                </tr>

                <tr>
                    <td style="padding: 40px 30px;">
                        <h1 style="color: #333333; font-size: 22px; margin-bottom: 20px; font-weight: 700;">Login Verification</h1>
                        
                        <p style="color: #666666; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                            Hello,
                        </p>
                        <p style="color: #666666; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                            We received a request to access your account. Please use the verification code below to complete your login.
                        </p>

                        <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 20px; text-align: center; margin-bottom: 30px;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #2c3e50; display: block;">
                                {otp_code}
                            </span>
                        </div>

                        <p style="color: #666666; font-size: 14px; line-height: 1.6;">
                            This code is valid for <strong>2 minutes</strong>. <br>
                            If you did not request this code, please ignore this email or contact support.
                        </p>
                    </td>
                </tr>

                <tr>
                    <td style="background-color: #f4f4f7; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                        <p style="color: #999999; font-size: 12px; margin: 0;">
                            &copy; 2026 Aiinhome Technology pvt ltd. All rights reserved.<br>
                            Need help? <a href="#" style="color: #2c3e50; text-decoration: none;">Contact Support</a>
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        if 200 <= response.status_code < 300:
            # Return a dictionary as per your previous requirement for consistent API responses
            return {"success": True, "message": "Email sent successfully"}
        else:
            print(f" SendGrid Failed. Status: {response.status_code}")
            return {"success": False, "message": f"SendGrid Error: {response.status_code}"}

    except Exception as e:
        print(f" Error sending Email via SendGrid: {str(e)}")
        return {"success": False, "message": str(e)}