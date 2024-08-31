import paramiko

ssh_host = "192.168.3.160"       # IP-адрес или доменное имя удаленного сервера
ssh_port = 22                    # Порт SSH (обычно 22)
ssh_user = "litho-proj-1"        # Имя пользователя SSH
ssh_password = "FIAN1234"        # Пароль пользователя SSH

def transfer_file(ssh_host, ssh_port, ssh_user, ssh_password, local_file, remote_file):

    # # Создание SSH-клиента
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # # Подключение к удаленному серверу
    print(f"Соединение с {ssh_host}...")
    ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
    print("Подключено.")
    
    try:
        # Создание SCP-клиента
        sftp = ssh.open_sftp()
        # Передача файла
        print(f"Передача {local_file} в {remote_file}...")
        sftp.put(local_file, remote_file)
        print("Передача завершена.")
    
    finally:
        # Закрытие SCP-клиента и SSH-сессии
        sftp.close()
        ssh.close()
        print("Соединение закрыто.")

# def execute_remote_command(host, port, username, password, command):
#     try:
#         # Создаем SSH-клиент
#         ssh = paramiko.SSHClient()

#         # Добавляем адрес удаленного сервера в список известных хостов
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#         # Подключаемся к удаленному хосту с использованием учетных данных
#         ssh.connect(hostname=host, port=port, username=username, password=password)

#         # Выполняем удаленную команду
#         stdin, stdout, stderr = ssh.exec_command(command)

#         # Получаем результат выполнения команды
#         result = stdout.read().decode('utf-8')
#         error = stderr.read().decode('utf-8')

#         # Закрываем SSH соединение
#         ssh.close()

#         return result, error

#     except Exception as e:
#         print(f"Ошибка: {e}")
#         return None, str(e)

local_file = "test1.png"   # Полный путь к Local файлу
remote_file = "/media/test1.png" # Полный путь и имя файла на удаленном сервере
transfer_file(ssh_host, ssh_port, ssh_user, ssh_password, local_file, remote_file)
