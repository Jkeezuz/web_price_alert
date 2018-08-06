import os

PASSWORD = os.environ.get('SMTP_PASS')
SUBJECT = 'PRICE ALERT'
EMAIL_ADDRESS = os.environ.get('SMTP_LOGIN')
ALERT_TIMEOUT = 0.01
COLLECTION = 'alerts'
