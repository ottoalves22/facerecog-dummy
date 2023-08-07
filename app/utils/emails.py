from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import utils.configs as configs

def send_email(email_recipient: str,
               email_subject: str,
               placeholders: Dict,
               attachment_location = ''):
    """
    template.html can have several placeholders to be replaced when sending email.
    ex: if you put <NAME> inside the html and creates the placeholders dict like:
    {'<NAME>': 'Joao'}, this tag will be replaced to Joao before sending the email.
    """
    email_sender = configs.smtp_user

    msg = MIMEMultipart('alternative')
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    with open('template.html', 'r') as f:
        html = f.read()

    for key in placeholders:
        html = html.replace(key, placeholders[key])

    msg.attach(MIMEText(html, 'html'))

    if attachment_location != '':
        filename = os.path.basename(attachment_location)
        attachment = open(attachment_location, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        "attachment; filename= %s" % filename)
        msg.attach(part)

    try:
        server = smtplib.SMTP(configs.smtp_host, int(configs.smtp_port))

        if configs.smtp_use_tls:
            server.starttls()

        server.login(configs.smtp_user, configs.smtp_pwd)
        server.sendmail(email_sender, email_recipient, msg.as_string())
        server.quit()
        return True
    except:
        return False