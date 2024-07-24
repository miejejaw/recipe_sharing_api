import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import format_html
from utils.jwt_token_utils import generate_jwt_token
import os

EMAIL_VERIFICATION_PATH = os.getenv('EMAIL_VERIFICATION_PATH')
FRONTEND_PASSWORD_REST_PATH = os.getenv('FRONTEND_PASSWORD_REST_PATH')

def send_email(html_content, subject, receiver_email):
    try:
        email = EmailMessage(
            subject = subject,
            body = html_content,
            to = [receiver_email],
        )
        
        email.content_subtype = 'html'
        email.send()
        return True
    
    except Exception as e:
        return False

def send_verification_email(user):
    payload = {
        'email': user.email,
        'id': str(user.id),
        'token_type': 'email_verification'
    }
    jwt_token = generate_jwt_token(payload)

    verification_url = EMAIL_VERIFICATION_PATH + jwt_token
    
    body = '''
            <p>Thank you for choosing PEN2TEXT!</p>
            <p>To finalize your registration and secure your account, we kindly ask you to verify your email address by clicking the link below:</p>
            <p>If you're unable to click the link, please copy and paste it into your browser's address bar.</p>
            <p>Please note that this verification link will expire after <span style="font-weight: 600; color: #1f1f1f;">5 minutes </span>  for security purposes.</p>
            <p>Once your email address is verified, you'll gain full access to all PEN2TEXT features and services.</p>
            <p>If you didn't sign up for a PEN2TEXT account, please disregard this email.</p>
            <p>For any questions or assistance, feel free to reach out to us.</p>
            <p>Best regards,<br>
           '''

    data = {
        'name': user.first_name + " " + user.last_name,
        'year': datetime.datetime.now().year,
        'date': datetime.date.today(),
        'messageType': "email verification",
        'body': format_html(body),
        'link': verification_url,
        'button_text': 'VERIFICATION LINK'
    }
    
    html_content = render_to_string('temp.html', data)
    subject = "Please Verify Your Email Address"
    receiver_email = user.email
    
    if send_email(html_content, subject, receiver_email):
        print("Email sent successfully!")
    else:
        print("Failed to send email.")

def send_reset_password_email(user):
    payload = {
        'email': user.email,
        'id': str(user.id),
        'token_type': 'password_reset'
    }
    jwt_token = generate_jwt_token(payload)
    reset_password_url = FRONTEND_PASSWORD_REST_PATH + jwt_token
    
    body = '''
                <p>Thank you for choosing PEN2TEXT!</p>
                <p>To reset your password and secure your account, we kindly ask you to verify your request by clicking the link below:</p>
                <p>If you're unable to click the link, please copy and paste it into your browser's address bar.</p>
                <p>Please note that this password reset link will expire after <span style="font-weight: 600; color: #1f1f1f;">5 minutes</span> for security purposes.</p>
                <p>Once your request is verified, you'll be able to set a new password and regain full access to all PEN2TEXT features and services.</p>
                <p>If you didn't request a password reset for your PEN2TEXT account, please disregard this email.</p>
                <p>For any questions or assistance, feel free to reach out to us.</p>
                <p>Best regards,<br>
            '''
    data = {
        'name': user.first_name + " " + user.last_name,
        'year': datetime.datetime.now().year,
        'date': datetime.date.today(),
        'messageType': "password reset email",
        'body': format_html(body),
        'link': reset_password_url,
        'button_text': 'RESET PASSWORD LINK'
    }
    
    
    html_content = render_to_string('temp.html', data)
    subject = "Password Reset"
    receiver_email = user.email
    
    if send_email(html_content, subject, receiver_email):
        return True
    else:
        return False