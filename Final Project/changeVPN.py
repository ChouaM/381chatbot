import paramiko
import Paramiko_Skills as s

def changeVPN1(newAdd):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    CSR1 = {'hostname':'192.168.56.101', 'port':'22', 'username':'cisco', 'password':'cisco123!', 'look_for_keys':'False', 'allow_agent':'False'} #s.get_list_from_file('ParaCSR1.txt')
    #print(f'Connecting to router {CSR1["hostname"]}')
    ssh_client.connect(**CSR1)
    shell = ssh_client.invoke_shell()

    #ssh_client = s.connect(**CSR1)
    #shell = s.get_shell(ssh_client)

    s.send_command(shell, 'enable')
    s.send_command(shell, 'cisco123!')
    s.send_command(shell, 'conf t')
    s.send_command(shell, 'no crypto isakmp key cisco address 172.16.0.2')
    s.send_command(shell, 'crypto isakmp key cisco address {}'.format(newAdd))
    s.send_command(shell, 'crypto map Crypt 10 ipsec-isakmp')
    s.send_command(shell, 'no set peer 172.16.0.2')
    s.send_command(shell, 'set peer {}'.format(newAdd))