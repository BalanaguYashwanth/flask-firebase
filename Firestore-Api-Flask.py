from flask import Flask,jsonify,request
from flask_restful import Resource,Api
import os
import pyrebase
import json
import firebase_admin
from firebase_admin import auth
from werkzeug.security import generate_password_hash
from firebase_admin import credentials, firestore, initialize_app
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
cred = credentials.Certificate('key.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
pb = pyrebase.initialize_app(json.load(open('fbconfig.json')))
todo_ref = db.collection('todos')


@app.route('/getcurrentuser',methods=['POST'])
def done():
    alldetails={}

    try:
        uid=request.json['uid']
        user = auth.get_user(uid)
        alldetails['uid']=user.uid
        alldetails['display_name']=user.display_name
        alldetails['email']=user.email
        alldetails['photo_url']=user.photo_url
        alldetails['owner']=user.custom_claims.get('owner')
        if user.custom_claims.get('admin'):
            alldetails['admin']=user.custom_claims.get('admin')
        else:
            alldetails['admin']=False    
        return alldetails
    except:
        return jsonify({'message':False}),400


@app.route('/updateuser',methods=['POST'])
def users():
    uid=request.json['uid']
    user=auth.update_user(
        uid,
        photo_url=request.json['photourl'],
        display_name=request.json['displayname'],
    )
    return 'done'


@app.route('/deletephoto/<object>',methods=['POST'])
def deleteimage(object):
    uid=request.json['uid']
    print(uid)
    user=db.collection(object).document(request.json['id']).update({
        "profilepic":request.json['photourl']
        })
    return 'updated'



@app.route('/signup',methods=['POST'])
def signup():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
       return jsonify({'message':'username and password must not in blank'}),400
    try:
        user = auth.create_user(
               email=email,
               password=password
        )
        print('user',user.uid)
        auth.set_custom_user_claims(user.uid, {'owner': True})
        return jsonify({'message': f'Successfully created user {user}'}),200
    except:
        return jsonify({'message': 'Error creating user'}),400


@app.route('/csignup',methods=['POST'])
def csignup():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
       return jsonify({'message':'username and password must not in blank'}),400
    try:
        user = auth.create_user(
               email=email,
               password=password
        )
        print('user',user.uid)
        auth.set_custom_user_claims(user.uid, {'owner': False})
        return jsonify({'message': f'Successfully created user {user}'}),200
    except:
        return jsonify({'message': 'Error creating user'}),400



@app.route('/asignup',methods=['POST'])
def asignup():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
       return jsonify({'message':'username and password must not in blank'}),400
    try:
        user = auth.create_user(
               email=email,
               password=password
        )
        print('user',user.uid)
        auth.set_custom_user_claims(user.uid, {'admin': True})
        return jsonify({'message': f'Successfully created user {user}'}),200
    except:
        return jsonify({'message': 'Error creating user'}),400


@app.route('/asignin',methods=['POST'])
def asignin():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
        return jsonify({'message':'username and password must not to be empty'})
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        arr=''
       
        for x in user:
            if x == 'localId':
                arr=(user[x])
                
        user1= auth.get_user(arr)
        user2=user1.custom_claims.get('admin')
        if user2:
            return user
        else:
            return jsonify({'message':'You are not admin to access it'}),400

    except:
        return jsonify({'message':'Error in logging user'}),400


@app.route('/signin',methods=['POST'])
def signin():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
        return jsonify({'message':'username and password must not to be empty'})
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        #user1=auth.get_user(user.uid)
        arr=''
       
        for x in user:
            if x == 'localId':
                arr=(user[x])
                
        user1= auth.get_user(arr)
        user2=user1.custom_claims.get('owner')
        print(user2)
        if user2:
            return user
        else:
            return jsonify({'message':'You are not owner to access it'}),400

    except:
        return jsonify({'message':'Error in logging user'}),400

@app.route('/csignin',methods=['POST'])
def csignin():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
        return jsonify({'message':'username and passowrd must not to be empty'}),400
    try:
        user = pb.auth().sign_in_with_email_and_password(email,password)
        carr=''
        
        for x in user:
            if x == 'localId':
                carr=(user[x])
                
        cuser1 = auth.get_user(carr)
        cuser2 = cuser1.custom_claims.get('owner')
        print(cuser2)
        if not cuser2:
            return user
        else:
            return jsonify({'message':'You are not customer to access it'}),400
    except:
        return jsonify({'message':'error in logging user'}),400


@app.route('/post/<object>', methods=['POST']) 
def create(object):
    """
        create() : Add document to Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    try:
        #id = request.json['id']
        db.collection(object).add(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/get/<object>', methods=['GET'])
def read(object):
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents
    """
    try:
        todo1={}
        # Check if ID was passed to URL query
        #todo_id = request.args.get('id')    
        if todo_ref:
            todo = db.collection(object).stream()

            for users in todo:
                #print( users.to_dict())
                todo1[users.id]=(users.to_dict())

            return jsonify(todo1), 200
        else:
            all_todos = [doc.to_dict() for doc in todo_ref.stream()]
            return jsonify(all_todos)
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        id = request.json['id']
        todo_ref.document(id).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/delete/<object>/<id>', methods=['GET', 'DELETE'])
def delete(object,id):
    """
        delete() : Delete a document from Firestore collection
    """
    try:
        # Check for ID in URL query
        #todo_id = request.args.get(id)
        db.collection(object).document(id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"


if __name__=="__main__":
    app.run(debug=True)

