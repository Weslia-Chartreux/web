import mimetypes
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart


def send_email_order(mail, id, name, des, money, img=False):
    load_dotenv()
    fr = 'wesbot63@gmail.com'
    ps = 'uGTPurKuJSZp7A7'
    msg = MIMEMultipart()
    msg['From'] = fr
    msg['To'] = mail
    msg['Subject'] = 'Покупка'
    text = f'''Вы заказали {name}
Описание: {des}
К оплате: {money}
id товара: {id}
Реквизиты: {'Здесь цифры'}
В комментариях пишите свой id'''
    msg.attach(MIMEText(text, 'plain'))
    if img:
        filename = os.path.basename(img)
        ctype, encoding = mimetypes.guess_type(img)
        maintype, subtype = ctype.split('/', 1)
        with open(img, mode='rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
        file.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(file)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(fr, ps)
    server.send_message(msg)
    server.quit()