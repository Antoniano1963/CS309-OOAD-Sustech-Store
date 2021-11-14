from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import aiosmtplib

from Store.settings import *

register = ''
change_pwd = ''
logo = None
logo_inv = None
with open('utils/email_templates/register.html', 'r') as f:
    register = f.read()
with open('utils/email_templates/change_password.html', 'r') as f:
    change_pwd = f.read()
with open('utils/email_templates/logoPure.4b5e7613.png', 'rb') as f:
    logo = MIMEImage(f.read())
    logo.add_header('Content-ID', '<image1>')
with open('utils/email_templates/logoPureInv.png', 'rb') as f:
    logo_inv = MIMEImage(f.read())
    logo_inv.add_header('Content-ID', '<image2>')


async def send_register_email(to: str, username: str, url: str) -> int:
    message_root = MIMEMultipart('related')
    message_root['From'] = formataddr([EMAIL_SENDER, EMAIL_HOST_USER])
    message_root['To'] = formataddr([username, to])
    message_root['Subject'] = Header('Store test')
    message_alternative = MIMEMultipart('alternative')
    message_root.attach(message_alternative)
    message_alternative.attach(MIMEText(register.format(username=username, url=url), _subtype='html', _charset='utf-8'))
    message_root.attach(logo)
    message_root.attach(logo_inv)
    server = aiosmtplib.SMTP(hostname=EMAIL_HOST, port=EMAIL_PORT, use_tls=False)
    try:
        await server.connect()
        await server.starttls()
        await server.login(username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
        _, result = await server.sendmail(EMAIL_HOST_USER, [to], message_root.as_string(), timeout=10)
        server.close()
        return True if result.find('Ok') >= 0 else False
    except Exception as e:
        print(e)
        server.close()
        return False


async def send_change_password_email(to: str, username: str, code: str) -> int:
    message_root = MIMEMultipart('related')
    message_root['From'] = formataddr([EMAIL_SENDER, EMAIL_HOST_USER])
    message_root['To'] = formataddr([username, to])
    message_root['Subject'] = Header('JCoder Change Password')
    message_alternative = MIMEMultipart('alternative')
    message_root.attach(message_alternative)
    message_alternative.attach(MIMEText(change_pwd.format(username=username, code=code), _subtype='html', _charset='utf-8'))
    message_root.attach(logo)
    message_root.attach(logo_inv)
    server = aiosmtplib.SMTP(hostname=EMAIL_HOST, port=EMAIL_PORT, use_tls=False)
    try:
        await server.connect()
        await server.starttls()
        await server.login(username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
        _, result = await server.sendmail(EMAIL_HOST_USER, [to], message_root.as_string(), timeout=10)
        server.close()
        return True if result.find('Ok') >= 0 else False
    except Exception as e:
        print(e)
        server.close()
        return False

