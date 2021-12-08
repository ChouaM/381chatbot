import paramiko
import time

def show_ip_int_brief(incoming_msg):
   
    #creating an ssh client object
    ssh_client = paramiko.SSHClient()

    #Save key for the first time
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


    #Connect to R1
    router = {'hostname': '192.168.56.101', 'port': '22', 'username':"cisco", 'password': 'cisco123!'}#dictionary
    ssh_client.connect(**router, look_for_keys=False, allow_agent=False)  
    print(f'Connecting to {router["hostname"]}')


    shell = ssh_client.invoke_shell()

    #execute the 'show run' command in R1, \n = pressing enter
    shell.send('enable\n')
    shell.send('cisco\n')
    shell.send('show ip int brief\n')

    #Sleep(wait to write the output)
    time.sleep(2)
    #format the output to UTF-8 & print it
    output = shell.recv(10000).decode('utf-8')
    #print(output)

    #Check if connection is active, T/F
    print(ssh_client.get_transport().is_active())

    #Closes connection
    print('Closing connection')
    ssh_client.close()

    return output