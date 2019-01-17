from flask import Flask, render_template, redirect, url_for,request,session,jsonify,flash
import requests
import unicodedata
import json,os

app = Flask(__name__)
app.config['SECRET_KEY'] = '\x17H\xb4\x1d\xa4\xa59VC\xc7\xe2d;O\xb1\xb9\xb4\x04\xdeM#\x8d\x9e\x03'


# @app.route('/signout')
# def signout():
#
#     return info.text

@app.route('/log')
def hell():
    session.clear()
    return render_template('firstView.html')

@app.route('/show')
def show():
    session.clear()
    return render_template('show.html')

@app.route('/')
def logout():
    message = " "

    session.clear()

    return render_template('loginPage.html', message=message)


token_ = ''
def keeptoken(gettoken,getname):
    global token_,username
    token_ = gettoken
    username = getname

    return gettoken

@app.route('/dashboard')
def dashboardww():
    session.clear()
    return redirect('/')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    global ff
    email = None
    tt = json.dumps(request.form)
    headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
    info = requests.post('http://localhost:5000/login', data=json.dumps(request.form), headers=headers)
    ff = info.text
    ww = info.text

    if (ww != 'Could not verify'):
             info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
             info = json.loads(info)
             name = info['admin']
             token = info['token']

             username = info['username']
             keeptoken(gettoken=token,getname=username)

             if (name == 1):

                 username = info['username']

                 info = requests.get('http://localhost:5000/allclients?token='+token_)
                 info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
                 data = json.loads(info)

                 info = requests.get('http://localhost:5000/user?token='+token_)
                 info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
                 data2 = json.loads(info)

                 # session.clear()
                 return render_template('show.html', info=data,info2=data2, mimetype='text/html', user=username)
             else:
                 username = info['username']
                 info = requests.get('http://localhost:5000/allclients?token='+token_)
                 info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
                 data = json.loads(info)

                 # session.clear()
                 return render_template('otheruserspage.html', info=data, mimetype='text/html', user=username)

    else:
             flash('Username or Password Incorrect, Check and Try Again')
             return render_template('loginPage.html')


@app.route('/createuser', methods=['POST'])
def createuser():

    headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
    requests.post('http://localhost:5000/user?token='+token_, data=json.dumps(request.form), headers=headers)

    info = requests.get('http://localhost:5000/allclients?token='+token_)

    if 'clients' in info.text:
        info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
        data = json.loads(info)

        flash("User Created Successfully")

        # session.clear()

        return render_template('show.html', info=data, mimetype='text/html', user=username)
    else:
        message = "Token Has Expire, Please Login Again"
        return render_template('loginPage.html', message2=message)


@app.route('/authuser', methods=['POST'])
def authuser():

    global ff
    email = None
    tt = json.dumps(request.form)
    headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json'}
    info = requests.post('http://localhost:5000/login', data=json.dumps(request.form), headers=headers)

    ff = info.text
    ww = info.text

    if (ww != 'Could not verify'):
        info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
        info = json.loads(info)
        name = info['admin']

        if (name == 1):
            token = info['token']
            username = info['username']
            keeptoken(gettoken=token,getname=username)
            info = requests.get('http://localhost:5000/allclients?token='+token_)
            info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
            data = json.loads(info)

            # session.clear()
            return render_template('create.html', info=data, mimetype='text/html', user=username)
        else:
            username = info['username']
            info = requests.get('http://localhost:5000/allclients?token='+token_)
            info = unicodedata.normalize('NFKD', info.text).encode('ascii','ignore')
            data = json.loads(info)

            # session.clear()
            return render_template('loginPage.html', info=data, mimetype='text/html', user=username)

    else:
        flash('Username or Password Incorrect, Check and Try Again')
        return render_template('loginPage.html')


@app.route('/deleteuser/<public_id>')
def delete_one_user(public_id):
    info = requests.get('http://localhost:5000/allclients/<public_id>?token='+token_)

    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=67)