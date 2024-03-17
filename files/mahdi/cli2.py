import requests
import json




import requests

URL = "http://127.0.0.1:5000/api/upload"







def upload(username,password,path):

    data = {"username": username, 'password' : password}
    file_path = path
    files = {'file': open(file_path, 'rb')}

    r = requests.post(URL, files=files  , data=data)

    if r.status_code == 200:
        result = r.json()
        print(result)
    else:
        print(f"Error: {r.status_code}, {r.text}")


def download(username,password,path):

    data = {"username": username, 'password' : password , "filename" : path}

    r = requests.post(URL  , data=data)

    if r.status_code == 200:
        result = r.json()
        print(result)
    else:
        print(f"Error: {r.status_code}, {r.text}")









upload('mahdi','123',"cli.py")
