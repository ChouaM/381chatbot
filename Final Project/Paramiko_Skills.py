import paramiko
import time
import ast

def connect(server_ip, server_port, user, passwd):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'Connecting to {server_ip}')
    ssh_client.connect(hostname=server_ip, port=server_port, username=user, password=passwd, look_for_keys=False,allow_agent=False)
    return ssh_client

def get_shell(ssh_client):
    shell = ssh_client.invoke_shell()
    return shell

def send_command(shell, command):
    print(f'Sending command: {command}')
    shell.send(command  + '\n')
    #time.sleep(timeout)

def show(shell,command, n=10000, timeout = 1):
    print(f'Sending command: {command}')
    shell.send('terminal length 0\n')
    shell.send(command  + '\n')
    time.sleep(timeout)
    output = shell.recv(n)
    output = output.decode()
    print (output)
    return output

def close(ssh_client):
    if ssh_client.get_transport().is_active()== True:
        print('Closing connection')
        ssh_client.close()

def get_list_from_file(filename):
    with open(filename) as f:
        data = ast.literal_eval(f.read())
        f.close()
        return data


