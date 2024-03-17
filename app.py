from flask import Flask, session ,request , jsonify as js , send_file
from ZDbyte import Zjson
import time , os
from werkzeug.utils import secure_filename


json_usr = Zjson()
json_usr.connectFile("usr/usr.json")

FILES_DIRECTORY = 'files'


app = Flask(__name__)
app.secret_key = 'de141738a55d3b32f25d365703a8322ccfe15123248e6f16'
app.config.update(
    DEBUG=True,
    HOST='0.0.0.0'
)


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
    """only check login"""

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
    
    if file.filename == '':
        return js({'success' : False , 'message': 'No selected file' , "data": {}}) , 404
    
    path = os.path.join(FILES_DIRECTORY+"/"+username, secure_filename(file.filename))
    file.save(path)

    if os.path.exists(path) == False:
        
        return js({'success' : False ,'message': '500 Internal Server Error' , "data" : {"filename" : secure_filename(file.filename)}}), 500


    return js({'success' : True ,'message': 'File uploaded successfully' , "data" : {"filename" : secure_filename(file.filename)}}) , 200







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




    file_path = os.path.join(FILES_DIRECTORY+"/"+username, filename)

    if not os.path.exists(file_path):
        return js({'success' : False ,'message': '404 File not exsist' , "data" : {"file_path" : file_path}}), 404


    return send_file(file_path, as_attachment=True)










if __name__ == '__main__':
    app.run()   