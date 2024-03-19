from flask import Flask, session ,request , jsonify as js , send_file , redirect
from ZDbyte import Zjson
import time , os
from werkzeug.utils import secure_filename
import hashlib


from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()







json_usr = Zjson()
json_usr.connectFile(THIS_FOLDER / "usr/usr.json")

json_index = Zjson()
json_index.connectFile(THIS_FOLDER / "config/index.json")



FILES_DIRECTORY = THIS_FOLDER / 'files'
LIB_DIRC = THIS_FOLDER / "lib"

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

def check_auth(username,password):
    if json_usr.exsist(username) == False:
        return js({'success' : False ,'message': '404 This account not exsist' , "data" : {"username" : username}}), 404

    usr_data = json_usr.read()[username]
    if usr_data['password'] != password:
        return js({'success' : False ,'message': '401 Forbidden' , "data" : {"username" : username}}), 403
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


@app.route('/')
def main():
    return redirect('/downloads')
@app.route('/downloads')
def downloads():
    return "<h1>Download .deb</h1>Cloud pype - cpype <br><br> <a href='/download/deb/0.0.1' >cpype-0.0.1.deb</a> for linux - last vertion <br><br><span>* required python3 for work</span>"

@app.route('/download/deb/<ver>')
def download_deb(ver):
    # Replace 'path/to/your/file.ext' with the actual path to your file
    filepath = LIB_DIRC / 'deb' / ver
    # Change 'filename.ext' to the name you want the downloaded file to have
    filename = f'cpipe-{ver}.deb'
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

    json_usr.append({username : {"password" : password , "time" : time.time() , "admin" : False}})
    if json_usr.exsist(username) == False:
        return js({'success' : False ,'message': '500 Internal Server Error' , "data" : {"username" : username}}), 500

    os.mkdir(f'{FILES_DIRECTORY}/{username}')

    return js({'success' : True ,'message': '201 User registered successfully' , "data" : {"username" : username}}), 201



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


    return js({'success' : True ,'message': '200 Ok' , "data" : {"username" : username}}), 200



@app.route('/api/info' , methods=['POST'])
def file_info():
    

    data = request.json
    req_data = ['username' , 'password','file_name','mode']
    req = check_req(req_data , data)
    if req != None:
        return req

    username = data.get('username')
    password = data.get('password')
    file_name = data.get('file_name')
    mode = data.get('mode')

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
                result.append((f,file_size,lst_modife,file_hash))

            return js({'success' : True ,'message': '200 Ok' , "data" : {"ls" : result}}), 200
        except:

            return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500
    if mode == 'get':

        try:
            index_data = json_index.read()
            if file_name not in index_data:
                return js({'success' : True ,'message': '404 File not exsist' , "data" : {"file_path" : file_name , "exsist" : False}}), 404


            if index_data[file_name]['public'] == False:
                return js({'success' : False ,'message': '403 this file is not public' , "data" : {"file_path" : file_name}}), 404
            auth = index_data[file_name]['auth']
            file_path  = os.path.join(FILES_DIRECTORY,auth,index_data[file_name]['path'])
            file_size = get_file_size(file_path)
            lst_modife =  os.path.getmtime(file_path)
            file_hash = get_file_hash(file_path)


            return js({'success' : True ,'message': '200 Ok' , "data" : {"info" : (index_data[file_name]['path'],file_size,lst_modife,auth),"hash" : file_hash , "exsist" : True }}), 200
        except:
            return js({'success' : False ,'message': '500 Internal server error' , "data" : {}}), 500



    lg = check_auth(username,password)
    if lg != True:
        return lg
    
    path = os.path.join(FILES_DIRECTORY,username, secure_filename(file_name))


    if os.path.exists(path) == False:
        return js({'success' : True ,'message': '200 Ok' , "data" : {"exsist" : False , "size" : None}}), 200


    file_size = get_file_size(path)

    

    file_hash = get_file_hash(path)

    return js({'success' : True ,'message': '200 Ok' , "data" : {"exsist" : True , "size" : file_size , 'hash' : file_hash}}), 200




@app.route('/api/upload', methods=['POST'])
def upload_file():

    if "username" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"username was not send"}}), 400
    if "password" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"password was not send"}}), 400


    username = request.form.get('username')
    password = request.form.get('password')

    lg = check_auth(username,password)
    if lg != True:
        return lg


    # ---------


    if 'file' not in request.files:
        return js({'success' : False , 'message': 'No file part' , "data" : {}}) , 404



    file = request.files['file']

    # file_hash = hashlib.sha256()
    # while True:
    #     chunk = file.read(4096)  # Read in 4KB chunks
    #     if not chunk:
    #         break
    #     file_hash.update(chunk)

    # file_hash_hexdigest = file_hash.hexdigest()



    if file.filename == '':
        return js({'success' : False , 'message': 'No selected file' , "data": {}}) , 404

    path = os.path.join(FILES_DIRECTORY,username, secure_filename(file.filename))
    file.save(path)


    # if get_file_hash(path) != file_hash_hexdigest:
    #     return js({'success' : False ,'message': 'Saving file on server problem' , "data" : {"filename" : secure_filename(file.filename)}}), 500

    file_hash_hexdigest = get_file_hash(path)
    if os.path.exists(path) == False:

        return js({'success' : False ,'message': '500 Internal Server Error' , "data" : {"filename" : secure_filename(file.filename)}}), 500


    return js({'success' : True ,'message': 'File uploaded successfully' , "data" : {"filename" : secure_filename(file.filename) , 'hash' : file_hash_hexdigest }}) , 200



@app.route('/api/download', methods=['GET'])
def download_file():

    if "username" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"username was not send"}}), 400
    if "password" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"password was not send"}}), 400
    if "filename" not in request.form :
        return js({'success' : False ,'message': '400 Invalid data format' , "data" : {"error":f"filename was not send"}}), 400

    username = request.form.get('username')
    password = request.form.get('password')
    filename = request.form.get('filename')

    lg = check_auth(username,password)
    if lg != True:
        return lg




    file_path = os.path.join(FILES_DIRECTORY,username, filename)

    if not os.path.exists(file_path):
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



    file_path = os.path.join(FILES_DIRECTORY,auth, file_name)

    if not os.path.exists(file_path):
        return js({'success' : False ,'message': '404 File not exsist' , "data" : {"file_path" : file_path , 'auth':auth}}), 404


    return send_file(file_path, as_attachment=True)










if __name__ == '__main__':
    app.run()
