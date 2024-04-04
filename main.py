import os
import smtplib as smtp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from dotenv import load_dotenv

load_dotenv()

def move_file(files: list[str], source_folder: str, target_folder: str):
    '''
    Перемещение файлов с одной директории в другую
    '''
    for file in files:
        source_file = os.path.join(source_folder, file)
        target_file = os.path.join(target_folder, file)
        os.rename(source_file, target_file)
        print(f'Файл {file} перемещен в {target_folder}')

def send_email(host: str, subject: str,
               to_addr: list[str], from_addr: str,
               body_text: str, source_folder: str, target_folder: str,
               login: str = None, password: str = None):
    '''
    Подготовка и отправка письма с вложением
    '''
    # Создание объекта письма
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ','.join(to_addr)
    msg['Subject'] = subject

    # Добавление тела письма
    msg.attach(MIMEText(body_text))

    # Получение списка файлов в исходной директории
    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

    # Перебор файлов и добавление их во вложения
    for file in files:
        # Открытие файла и чтение его содержимого
        with open(os.path.join(source_folder, file), 'rb') as attach:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attach.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                'attachment',
                filename=file
            )
            msg.attach(part)
    
    # Отправка письма
    try:
        with smtp.SMTP_SSL(host) as server:
            # server.set_debuglevel(2)
            # server.ehlo(from_addr)
            if login and password:
                server.login(login, password)
            # server.auth_plain()
            server.sendmail(from_addr, to_addr, msg.as_string())
            print('Отправлено!')
        # Перемещение отправленных файлов в директорию для отправленных
        move_file(files, source_folder, target_folder)
    except Exception as e:
        print(f'Ошибка отправки: {e}')

if __name__ == "__main__":
    # Почтовые настройки (получаем из переменных окружения)
    host = os.getenv('HOST')
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    from_addr = os.getenv('FROM')
    to_addr = ['seregs08@qip.ru']   # Список адресов получателей
    subject = 'Тестовое письмо'
    body_text = 'Тестовый текст письма'
    src_folder = '/home/sergo/SendEmail/TestFolder'         # Директория с файлами
    trgt_folder = '/home/sergo/SendEmail/TestFolder/Sender' # Директория для перемещщения отправленных файлов
    send_email(host, subject, to_addr, from_addr, body_text, src_folder, trgt_folder, login, password)