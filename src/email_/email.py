import smtplib  
import ssl  
import random  
from utils import encrypt_file, decrypt_file #type: ignore

from config import Config
SERVER_NAME = Config.SERVER_NAME
HTTP_STATUS = Config.HTTP_STATUS

class Email:

    def __init__(self):
        self.port = 465
        self.smtp_server = 'smtp.gmail.com'
        self.context = ssl.create_default_context()
        self.sender_id = 'help.creativenames@gmail.com'
        
        try:
            decrypt_file('assets/password.txt')
        except Exception as e:
            print(e)

        with open('assets/password.txt', 'r') as f:
            self.password = f.readlines()[0]
            
        encrypt_file('assets/password.txt')

    def send_email(self, heading, content, EmailID):
        message = f"Subject: {heading}\n\n{content}"
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=self.context) as server:
            server.login(self.sender_id, self.password)
            server.sendmail(self.sender_id, EmailID, message)

    def send_registration_otp(self, EmailID):
        self.reg_otp = ''
        while len(self.reg_otp) < 5:
            self.reg_otp += str(random.randint(0, 9))

        heading = f'OTP for signing up on {HTTP_STATUS}{SERVER_NAME}'
        content = f'Hey! Your OTP for signing up on {HTTP_STATUS}{SERVER_NAME} is {self.reg_otp}'

        self.send_email(heading, content, EmailID)

        return self.reg_otp

    def send_recovery_password(self, EmailID):
        self.reco_otp = ''
        while len(self.reco_otp) < 5:
            self.reco_otp += str(random.randint(0, 9))

        heading = f'OTP for recovering your account on {HTTP_STATUS}{SERVER_NAME}'
        content = f'Hey! Your OTP for recovering your account\'s password on {HTTP_STATUS}{SERVER_NAME} is {self.reco_otp}'

        self.send_email(heading, content, EmailID)

        return self.reco_otp

