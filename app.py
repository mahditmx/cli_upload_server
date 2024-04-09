import hashlib
import os
from pathlib import Path
import time
import secrets
import string
from ZDbyte import Zjson
from flask import Flask, jsonify as js, redirect, request, send_file, session
from werkzeug.utils import secure_filename
import magic
import json




THIS_FOLDER = Path(__file__).parent.resolve()







json_usr = Zjson()
json_usr.connectFile(THIS_FOLDER / "usr/usr.json")

json_index = Zjson()
json_index.connectFile(THIS_FOLDER / "config/index.json")


FILES_DIRECTORY = THIS_FOLDER / 'files'
LIB_DIRC = THIS_FOLDER / "lib"
USR_CONF_DIR = THIS_FOLDER / 'usr_config'

# json_usr = Zjson()
# json_usr.connectFile("usr/usr.json")

# json_index = Zjson()
# json_index.connectFile("config/index.json")



# FILES_DIRECTORY = 'files'


app = Flask(__name__)
app.secret_key = 'de141738a55d3b32f25d365703a8322ccfe15123248e6f16'
app.config.update(
    DEBUG=True,
    HOST='0.0.0.0'
)
def list_files(directory):
    files = []
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files
def get_file_size(file_path):
    try:
        # Get the size of the file in bytes
        size = os.path.getsize(file_path)
        return size
    except OSError:
        # Handle any potential errors, such as the file not existing
        print("Error: Unable to get file size.")
        return None
def check_req(req:list , data):
    for d in req:
        if d not in data:
            return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"{d} was not send"}}), 400

def check_auth(username,password=None,token=None):

    if token == None:
        if json_usr.exsist(username) == False:
            return js({'success' : False ,'message': '404 This account not exsist' , "data" : {"username" : username}}), 404

        usr_data = json_usr.read()[username]
        if usr_data['password'] != password:
            return js({'success' : False ,'message': '401 Forbidden' , "data" : {"username" : username}}), 403
        return True
    if password == None and token != None:
        if json_usr.exsist(username) == False:
            return js({'success' : False ,'message': '404 This account not exsist' , "data" : {"username" : username}}), 404

        usr_data = json_usr.read()[username]
        usr_token = usr_data['token'][0]
        if usr_token != token:
            return js({'success' : False ,'message': f'401 Forbidden {token}' , "data" : {"username" : username}}), 403
        return True



def get_file_hash(file_path):
    # Initialize the hash object
    file_hash = hashlib.sha256()

    # Open the file in binary mode and calculate the hash
    with open(file_path, "rb") as f:
        while True:
            # Read the file in chunks
            chunk = f.read(4096)
            if not chunk:
                break
            # Update the hash object with each chunk of data
            file_hash.update(chunk)

    # Retrieve the hexadecimal digest of the hash
    file_hash_hexdigest = file_hash.hexdigest()
    
    return file_hash_hexdigest
def generate_token(length=24):
    """Generate a random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_public_file(file_name,mode='return'):
    try:
        index_data = json_index.read()
        if file_name not in index_data:
            return js({'success' : True ,'message': '404 File not exsist' , "data" : {"file_path" : file_name , "exsist" : False}}), 404


        if index_data[file_name]['public'] == False:
            return js({'success' : False ,'message': '403 this file is not public' , "data" : {"file_path" : file_name}}), 404
        auth = index_data[file_name]['auth']
        filename = index_data[file_name]['path']

        dot_index = filename.rfind('.')
        if dot_index != -1:
            output =  filename[:dot_index] + '.zip'
        else:
            output = filename + '.zip'



        file_path  = os.path.join(FILES_DIRECTORY,auth,filename)
        zip_path  = os.path.join(FILES_DIRECTORY,auth,output)






        usr_conf_dir = os.path.join(USR_CONF_DIR,auth)
        usr_conf_zip = os.path.join(USR_CONF_DIR,auth,'zip.json')

        json_zip = Zjson()
        json_zip.connectFile(usr_conf_zip)
        zip_info = json_zip.read()



        ziped = False
        if not os.path.exists(file_path):
            if os.path.exists(zip_path):
                file_path = zip_path
                ziped = True

                if not output in zip_info : 
                    if mode == 'init':
                        return 404
                    return js({'success' : True ,'message': '404 File not exsist' , "data" : {"file_path" : file_name , "exsist" : False}}), 404

                file_hash = zip_info[output]['hash']


            else:
                if mode == 'init':
                    return 404
                return js({'success' : True ,'message': '404 File not exsist' , "data" : {"file_path" : file_name , "exsist" : False}}), 404

    
        file_size = get_file_size(file_path)
        lst_modife =  os.path.getmtime(file_path)
        if not ziped:
            file_hash = get_file_hash(file_path)


        if mode == 'init':
            
            return {"info" : (filename,file_size,lst_modife,auth),"hash" : file_hash , "exsist" : True , 'ziped' : ziped }
        return js({'success' : True ,'message': '200 Ok' , "data" : {"info" : (filename,file_size,lst_modife,auth),"hash" : file_hash , "exsist" : True , 'ziped' : ziped }}), 200
    except:
        if mode == 'init':
            return False
        return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500




@app.route('/')
def main():
    return redirect('/downloads')
@app.route('/downloads')
def downloads():
    return """<h1>Download .deb</h1>Cloud database - Cbase 
    <br><br> <a href='/download/deb/0.0.4' >cbase-0.0.4.deb</a> for linux 8.2MB e06b4a06ed6d88cbe11b9e1ff94a030f3d099038bda8e3096d599643a38c779e   - Last version
    <br> <a href='/download/deb/0.0.3' >cbase-0.0.3.deb</a> for linux 8.2MB 3ec0df369cfd3ae4258a62a06835d325be8b7f24212ed5de9482f99ccca050ba
    <br> <a href='/download/deb/0.0.2' >cbase-0.0.2.deb</a> for linux 8.2MB 8641ef435e65ab9e862200a959595c2a0e6727c9b479a8cbe56389d39cb2d734
    
    <br><br><br>
    
    <h2>Get update from <font color="#26A269">cbase</font></h2>

    <pre> <font color="#26A269">$</font> cbase get cbase</pre>

    <br>
    <h3>output</h3>
<pre><font color="#A347BA">dev@usr</font> <font color="#12488B">~</font>$ <font color="#26A269">cbase</font> get cbase                                                                                         
geting <font color="#A347BA">cbase</font> info...
[<font color="#A2734C">ZIP</font>] File ziped on the server
<font color="#2AA1B3">cbase-0.0.3.deb</font> hash : 3ec0df369cfd3ae4258a62a06835d325be8b7f24212ed5de9482f99ccca050ba
	are you shure to download <font color="#2AA1B3">cbase-0.0.3.deb </font><font color="#A347BA">(8.17 MB)</font> published by <font color="#A2734C"><b>cbase</b></font> [Y/n] ? y
downloading <font color="#A347BA">cbase-0.0.3.deb</font>...
	 <font color="#12488B">56.44</font><font color="#2AA1B3"> %</font> <font color="#12488B">━━━━━━━━━━━━━━━━━━━━━━━━━━━━</font><font color="#171421">━━━━━━━━━━━━━━━━━━━━━━</font> <font color="#12488B">4.61</font><font color="#2AA1B3">/</font><font color="#A347BA">8.17 MB</font> [<font color="#2AA1B3">Speed</font>: 102.30 KB/s]  </pre>



    """

@app.route('/download/deb/<ver>')
def download_deb(ver):
    # Replace 'path/to/your/file.ext' with the actual path to your file
    filepath = LIB_DIRC / 'deb' / ver
    # Change 'filename.ext' to the name you want the downloaded file to have
    filename = f'cbase-{ver}.deb'
    path = os.path.join(filepath ,filename)
    # return str(path)
    return send_file(path, as_attachment=True)







@app.route('/api/crAcc' , methods=['POST'])
def createAccount():
    data = request.json
    req_data = ['username' , 'password']
    req = check_req(req_data , data)
    if req != None:
        return req

    username = data.get('username')
    password = data.get('password')
    if json_usr.exsist(username) == True:
        return js({'success' : False ,'message': '409 This username allready exsist' , "data" : {"username" : username}}), 409

    usr_token = generate_token(length=32)
    usr_token_Expiration = time.time() + 7892000 # ~ 3 month

    json_usr.append({username : {"password" : password , "time" : time.time() , "admin" : False , 'token' : [usr_token , usr_token_Expiration]}})
    if json_usr.exsist(username) == False:
        return js({'success' : False ,'message': '500 Internal Server Error' , "data" : {"username" : username}}), 500

    os.mkdir(f'{FILES_DIRECTORY}/{username}')
    os.mkdir(f'{USR_CONF_DIR}/{username}')
    with open(f'{USR_CONF_DIR}/{username}/zip.json','w+') as f:
        f.write('{}')

    return js({'success' : True ,'message': '201 User registered successfully' , "data" : {"username" : username , 'token' : usr_token}}), 201



@app.route('/api/login' , methods=['POST'])
def check_login():
    """only check auth"""

    data = request.json
    req_data = ['username' , 'password']
    req = check_req(req_data , data)
    if req != None:
        return req

    username = data.get('username')
    password = data.get('password')

    lg = check_auth(username,password)
    if lg != True:
        return lg



    usr_conf_dir = os.path.join(USR_CONF_DIR,username)
    usr_conf_zip = os.path.join(USR_CONF_DIR,username,'zip.json')

    if not os.path.exists(usr_conf_dir) : 
        os.mkdir(usr_conf_dir)
        with open(usr_conf_zip,'w+') as f :
            f.write("{}")


    usr_info = json_usr.read()
    if "token" in usr_info[username]:
        if usr_info[username]['token'][1] <= time.time():
            usr_token = generate_token(length=32)
            usr_token_Expiration = time.time() + 7892000 # ~ 3 month
            json_usr.append({username : {"password" : password , "time" : time.time() , "admin" : False , 'token' : [usr_token , usr_token_Expiration]}})
            return js({'success' : True ,'message': '200 Ok' , "data" : {"username" : username , "token" : usr_token}}), 200
        else:
            return js({'success' : True ,'message': '200 Ok' , "data" : {"username" : username , "token" : usr_info[username]['token'][0]}}), 200
    else:
        usr_token = generate_token(length=32)
        usr_token_Expiration = time.time() + 7892000 # ~ 3 month 
        json_usr.append({username : {"password" : password , "time" : time.time() , "admin" : False , 'token' : [usr_token , usr_token_Expiration]}})

        return js({'success' : True ,'message': '200 Ok' , "data" : {"username" : username , "token" : usr_token}}), 200




@app.route('/api/rm_file' , methods=['POST'])
def rm_file():
    """only check auth"""

    data = request.json
    req_data = ['username', 'token', 'file_name']
    req = check_req(req_data , data)
    if req != None:
        return req

    username = data.get('username')
    token = data.get('token')
    filename = data.get('file_name')


    lg = check_auth(username,token=token)
    if lg != True:
        return lg


    file_path  = os.path.join(FILES_DIRECTORY,username,filename)

    if not os.path.exists(file_path):
        return js({'success' : False ,'message': '404 File was not exsist' , "data" : {"file_path" : filename }}), 404


    os.remove(file_path)
    if not os.path.exists(file_path):
        return js({'success' : True ,'message': 'File remove successfully' , "data" : {"file_path" : filename }}), 200
    

    return js({'success' : False ,'message': '500 Something went wrong' , "data" : {"file_path" : filename }}), 500


















@app.route('/api/pub' , methods=['POST'])
def indexing():

    data = request.json
    req_data = ['username' , 'token' , "file_name" , "f_name" , "force"]
    req = check_req(req_data , data)
    if req != None:
        return req

    username = data.get('username')
    token = data.get('token')
    file_name = data.get('file_name')
    f_name = data.get('f_name')
    force = data.get('force')

    lg = check_auth(username,token=token)
    if lg != True:
        return lg



    
    file_path  = os.path.join(FILES_DIRECTORY,username,file_name)

    dot_index = file_path.rfind('.')
    if dot_index != -1:
        output =  file_path[:dot_index] + '.zip'
    else:
        output = file_path + '.zip'

    if not os.path.exists(file_path) and not os.path.exists(output):
        return js({'success' : False ,'message': '404 File not exsist' , "data" : {"file_path" : file_name , "exsist" : False}}), 404


    index_data = json_index.read()
    if f_name in index_data:
        if index_data[f_name]['auth'] != username:
            return js({'success' : False ,'message': '403 this file allready exsist and you dont have permition' , "data" : {"username" : username, 'per': False}}), 403
        elif force == False:
            return js({'success' : False ,'message': '401 this file allready exsist' , "data" : {"username" : username , 'per': True}}), 401


    index = {}
    index[f_name] = {
        "auth" : username,
        "path" : file_name,
        "public" : True
    }
    try:
        json_index.append(index)
    except:
        return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500



    return js({'success' : True ,'message': f'{file_name} publish as {f_name}' , "data" : {"username" : username}}), 200


@app.route('/api/info' , methods=['POST'])
def file_info():
    

    data = request.json
    req_data = ['username','token','file_name','mode']
    req = check_req(req_data , data)
    if req != None:
        return req

    username = data.get('username')
    token = data.get('token')
    file_name = data.get('file_name')
    mode = data.get('mode')

    if mode == 'get_ls':

        # try:
            path = os.path.join(FILES_DIRECTORY,username)
            index_data = json_index.read()

            result = {}
            for pub in index_data:
                pub_data = get_public_file(pub,mode='init')
                result[pub] = pub_data





            return js({'success' : True ,'message': '200 Ok' , "data" : result}), 200
    
            exit()
        # except:

            # return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500



        # return {"success" : True , 'data' : data}











    if mode == 'get':
        re = get_public_file(file_name)
        return re





    lg = check_auth(username,token=token)
    if lg != True:
        return lg
    

    if mode == "all" : 
        try:
            path = os.path.join(FILES_DIRECTORY,username)
            files = list_files(path)
            result = []
            for f in files:
                file_path  = os.path.join(FILES_DIRECTORY,username,f)
                file_size = get_file_size(file_path)
                lst_modife =  os.path.getmtime(file_path)
                file_hash =  get_file_hash(file_path)

                usr_conf_dir = os.path.join(USR_CONF_DIR,username)
                usr_conf_zip = os.path.join(USR_CONF_DIR,username,'zip.json')

                json_zip = Zjson()
                json_zip.connectFile(usr_conf_zip)
                zip_info = json_zip.read()


                oldname = None
                if f in zip_info:
                    oldname = f
                    f = zip_info[oldname]['orgname']
                    file_hash = zip_info[oldname]['hash']

                result.append((f,file_size,lst_modife,file_hash,oldname))

            return js({'success' : True ,'message': '200 Ok' , "data" : {"ls" : result}}), 200
        except:

            return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500

    if mode == 'hash':
        try:
            path = os.path.join(FILES_DIRECTORY,username)
            files = list_files(path)
            result = []
            for f in files:
                file_path  = os.path.join(FILES_DIRECTORY,username,f)
                file_hash =  get_file_hash(file_path)
                if file_hash == file_name: # file_name here mean hash send from client
                    file_size = get_file_size(file_path)
                    lst_modife =  os.path.getmtime(file_path)
                    result.append((f,file_size,lst_modife,file_hash))

            usr_conf_zip = os.path.join(USR_CONF_DIR,username,'zip.json')
            json_zip = Zjson()
            json_zip.connectFile(usr_conf_zip)
            zip_info = json_zip.read()
            for v , k in zip_info.items():
                f = k['orgname']
                file_path  = os.path.join(FILES_DIRECTORY,username,v)

                if not os.path.exists(file_path) :
                    continue # TODO: remove file from zip_json
                file_hash = k['hash']
                oldname = v

                file_size = get_file_size(file_path)
                lst_modife =  os.path.getmtime(file_path)
                if k['hash'] == file_name: # file_name here mean hash send from client
                    result.append((f,file_size,lst_modife,file_hash,oldname))



            return js({'success' : True ,'message': '200 Ok' , "data" : {"ls" : result}}), 200
        except:

            return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500




    sec_file_name = secure_filename(file_name)
    path = os.path.join(FILES_DIRECTORY,username, sec_file_name)


    dot_index = sec_file_name.rfind('.')
    if dot_index != -1:
        output =  sec_file_name[:dot_index] + '.zip'
    else:
        output = sec_file_name + '.zip'
    path_zip = os.path.join(FILES_DIRECTORY,username, output)


    usr_conf_zip = os.path.join(USR_CONF_DIR,username,'zip.json')
    json_zip = Zjson()
    json_zip.connectFile(usr_conf_zip)
    zip_info = json_zip.read()

    if os.path.exists(path_zip):


        file_size = get_file_size(path_zip)
        file_hash = zip_info[output]['hash']

        return js({'success' : True ,'message': '200 Ok' , "data" : {"exsist" : True , "size" : file_size , 'hash' : file_hash , 'ziped' : True}}), 200



    elif not os.path.exists(path):




        for k , v in zip_info.items():
            if v['orgname'] == sec_file_name:
                file_size = get_file_size(path)
                return js({'success' : True ,'message': '200 Ok' , "data" : {"exsist" : True , "size" : file_size , 'hash' : v['hash'] , 'ziped' : True}}), 200
            
        






        return js({'success' : True ,'message': '200 Ok' , "data" : {"exsist" : False , "size" : None}}), 200


    file_size = get_file_size(path)
    file_hash = get_file_hash(path)

    return js({'success' : True ,'message': '200 Ok' , "data" : {"exsist" : True , "size" : file_size , 'hash' : file_hash , 'ziped' : False}}), 200



def check_media_file_content(file):
    allowed_media_types = {'video/', 'audio/', 'image/'}
    file_type = magic.Magic(mime=True).from_buffer(file.read(1024))
    file.seek(0)  # Reset file pointer
    return any(file_type.startswith(media_type) for media_type in allowed_media_types)
def check_archive_file_content(file):
    allowed_archive_types = {'application/zip', 'application/x-rar-compressed', 'application/gzip'}
    file_type = magic.Magic(mime=True).from_buffer(file.read(1024))
    file.seek(0)  # Reset file pointer
    return file_type in allowed_archive_types



@app.route('/api/upload', methods=['POST'])
def upload_file():

    if "username" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"username was not send"}}), 400
    if "token" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"token was not send"}}), 400
    if "zip" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"zip was not send"}}), 400
    if "filename" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"filename was not send"}}), 400
    if "org-hash" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"org-hash was not send"}}), 400


    username = request.form.get('username')
    token = request.form.get('token')
    zip_ = request.form.get('zip')
    filename = request.form.get('filename')
    org_hash = request.form.get('org-hash')

    print('*---*---')
    print(zip_)
    print(filename)
    print(org_hash)
    print('*---*---')

    lg = check_auth(username,token=token)
    if lg != True:
        return lg


    # ---------


    if 'file' not in request.files:
        return js({'success' : False , 'message': 'No file part' , "data" : {}}) , 404



    file = request.files['file']



    if file.filename == '':
        return js({'success' : False , 'message': 'No selected file' , "data": {}}) , 404



    if not check_media_file_content(file):
        if not check_archive_file_content(file):
            return js({'success' : False ,'message': 'File type not allowed - use last offical client', "data": {}}) , 403


    file_name = secure_filename(file.filename)


    path = os.path.join(FILES_DIRECTORY, username, file_name)
    file.save(path)


    file_hash_hexdigest = get_file_hash(path)

    if zip_:
        usr_conf_dir = os.path.join(USR_CONF_DIR,username)
        usr_conf_zip = os.path.join(USR_CONF_DIR,username,'zip.json')

        if not os.path.exists(usr_conf_dir) : 
            os.mkdir(usr_conf_dir)
            with open(usr_conf_zip,'w+') as f :
                f.write("{}")


        json_zip = Zjson()
        json_zip.connectFile(usr_conf_zip)
        json_zip.append({file_name : {'orgname' : filename, 'hash' : org_hash}})


    if os.path.exists(path) == False:

        return js({'success' : False ,'message': '500 Internal Server Error' , "data" : {"filename" : secure_filename(file.filename)}}), 500


    return js({'success' : True ,'message': 'File uploaded successfully' , "data" : {"filename" : secure_filename(file.filename) , 'hash' : file_hash_hexdigest }}) , 200



@app.route('/api/download', methods=['GET'])
def download_file():

    if "username" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"username was not send"}}), 400
    if "token" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"token was not send"}}), 400
    if "filename" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"filename was not send"}}), 400

    username = request.form.get('username')
    token = request.form.get('token')
    filename = request.form.get('filename')

    lg = check_auth(username,token=token)
    if lg != True:
        return lg




    file_path = os.path.join(FILES_DIRECTORY,username, filename)


    dot_index = filename.rfind('.')
    if dot_index != -1:
        output =  filename[:dot_index] + '.zip'
    else:
        output = filename + '.zip'
    file_path_zip = os.path.join(FILES_DIRECTORY,username, output)

    if os.path.exists(file_path_zip):
        return send_file(file_path_zip, as_attachment=True)


    elif not os.path.exists(file_path):
        return js({'success' : False ,'message': '404 File not exsist' , "data" : {"file_path" : file_path}}), 404


    return send_file(file_path, as_attachment=True)




@app.route('/api/get', methods=['GET'])
def get_file():


    if "filename" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"filename was not send"}}), 400


    filename = request.form.get('filename')


    index_data = json_index.read()
    if filename not in index_data:
        return js({'success' : False ,'message': '404 File not exsist' , "data" : {"file_path" : filename}}), 404


    if index_data[filename]['public'] == False:
        return js({'success' : False ,'message': '403 this file is not public' , "data" : {"file_path" : filename}}), 404
    auth = index_data[filename]['auth']
    file_name = index_data[filename]['path']

    dot_index = file_name.rfind('.')
    if dot_index != -1:
        output =  file_name[:dot_index] + '.zip'
    else:
        output = file_name + '.zip'
    file_path_zip = os.path.join(FILES_DIRECTORY,auth, output)


    if os.path.exists(file_path_zip):
        return send_file(file_path_zip, as_attachment=True)


    file_path = os.path.join(FILES_DIRECTORY,auth, file_name)

    if not os.path.exists(file_path):
        return js({'success' : False ,'message': '404 File not exsist' , "data" : {"file_path" : file_path , 'auth':auth}}), 404


    return send_file(file_path, as_attachment=True)










if __name__ == '__main__':
    app.run()
