from flask import (Flask, render_template,
                   request, session, redirect, url_for,
                   flash, jsonify, send_file)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from forms import (SignupForm, LoginForm,
                   UploadForm)
from uuid import uuid4
from datetime import datetime
import re
import random
from string import punctuation
from io import BytesIO
from models.users import User
from models.quotes import Quote
from models.quoteToPic import GenImage
from models.database import Database


app = Flask(__name__)

Database.initialize('iThinketh')

app.config['SECRET_KEY'] = '{}'.format(uuid4().hex)
bootstrap = Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
moment = Moment(app)


@app.before_request
def make_session_permanent():
    session.permanent = True


def getCUserData():
    secret_cookie = session.get('_cu')
    return User.verifySession(secret_cookie)


app.jinja_env.globals.update(getCUserData=getCUserData)


@app.route("/")
def index():
    quotes = Quote.GetAllQuotes()
    try:
        first = [quotes[random.randint(0, len(quotes)-1)]]
        print(first)
    except:
        first = []

    return render_template('index.html', quotes=quotes, first=first)


@app.route("/quotes/<string:quoteID>")
@app.route("/quotes")
def quotes(quoteID=None):
    if quoteID and quoteID.isalnum():
        q = User.getQuotebyQuoteID(quoteID)
        if q:
            cu = getCUserData()
            if cu:
                if q.get('userID') == cu.get('_id'):
                    loggedIn = "true"
                    current_usr = cu
            else:
                loggedIn = 'false'
                current_usr = {}

            return render_template('post.html', QuoteData=q,
                                   loggedIn=loggedIn,
                                   current_usr=current_usr)

        else:
            flash('Invalid Quote ID!')
            return redirect('/', 302)


@app.route('/quotes/images/<string:quoteID>')
@app.route('/quotes/images/download/<string:quoteID>')
def downloadQuote(quoteID):
    if quoteID:
        q = User.getQuotebyQuoteID(quoteID)
        if q:
            quote = q.get('quote')
            author = q.get('name').title()
            if 'download' in request.path:
                download = True
                User.updateDownloads(q.get('userID'), quoteID)
            else:
                download = False
            return send_file(
                GenImage(quote, author, q.get('quoteID')),
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f"{q.get('name').title()}\'s Quote - \
iThinketh.jpeg")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if session.get('_cu', None) == None:
            form = LoginForm()
            # If Post Method is used..
            if form.validate() == False:
                # if form validation fails..
                return render_template('login.html', form=form)
            else:
                # Regular Expression for checking email syntax
                isEmail = re.compile(r"[^@]+@[^@]+\.[^@]+")

                if isEmail.fullmatch(form.username.data):
                    # flash('Email detected!')
                    result = User.checkUser(
                        username=form.username.data.lower(),
                        password=form.password.data,
                        email=True)
                else:
                    result = User.checkUser(
                        username=form.username.data.lower(),
                        password=form.password.data)

                if result:
                    new_session = User.createSession(result)
                    session['_cu'] = new_session

                    return redirect('/profile/')

                elif result is False:
                    flash('Invalid Password! Try Again..')

                else:
                    flash('User Does not Exist! Please Check your \
Email Address or Username and Try Again..')

                return redirect(url_for('login'))

        else:
            return redirect(url_for('index'))

    elif request.method == 'GET':
        return render_template('login.html', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            result = User.checkUser(
                username=form.email.data,
                password=form.password.data,
                signUp=True,
                email=True)

            if result:
                flash(
                    'User Already Exists! Please Login or Use \
different email address..')
                return redirect(url_for('signup'))

            else:
                newUser = User(name=form.name.data.lower(),
                               email=form.email.data.lower(),
                               username=form.username.data.lower(),
                               about=form.about.data,
                               password=form.password.data)
                newUser.saveUser()
                flash('Account Created Successfully! Now go to the login page\
 to Login into your account.')
                return redirect(url_for('index'))

    elif request.method == 'GET':
        session['username'] = None
        return render_template('signup.html', form=form)


@app.route("/logout")
def logout():
    cu = session.pop('_cu', None)
    if cu:
        User.removeSession(cu)
        flash('You are Logged out!')
    else:
        flash('You were not Logged In!')

    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route("/profile/<string:username>")
@app.route("/profile/")
def profile(username=None):

    if session.get('_cu', None) is None and username is not None:
        if any(char in punctuation.replace('_', '') for char in username):
            flash('Invalid Username!')
            return redirect(url_for('index'))
        else:
            current_usr = {}

    elif username is None and session.get('_cu', None):
        return redirect(f'/profile/{getCUserData().get("username")}', 302)

    elif username and session.get('_cu', None):
        # if getCUserData().get('username') == username:
        current_usr = getCUserData()

    dataToDisplay = User.getUserByUsername(username)

    if dataToDisplay:
        quotes = list(Quote.GetQuotesByUserID(dataToDisplay.get('_id')))
        return render_template('profile.html',
                               userData=dataToDisplay,
                               current_usr=current_usr,
                               quotes=quotes,
                               current_time=datetime.utcnow())
    else:
        return redirect('/'), 404, {"Refresh": "2; url=/"}


@app.route("/settings/")
def settings():
    if session.get('_cu'):
        dataToDisplay = getCUserData()
        return render_template('settings.html',
                               userData=dataToDisplay,
                               current_time=datetime.utcnow())
    else:
        flash('Please Login to Access Settings Page!')
        return redirect('/login', 302)


@app.route('/api/quote', methods=['POST', 'PUT', 'DELETE'])
@app.route('/api', methods=['POST', 'PUT', 'DELETE'])
def api():
    current_session = session.get('_cu')

    if current_session:
        data = request.json
        if data:
            print(data)
            result = None
            if 'quote' in request.path:
                print('path : quotes')
                if request.method == 'PUT':
                    quote_ = data.get('quote')
                    if len(quote_.strip()) < 1:
                        flash('Quote cannot be empty!')
                        return jsonify({'error': 'quote can\'t be empty'})

                    quoteID = data.get('quoteID')
                    qobj = User.getQuotebyQuoteID(quoteID)
                    if qobj.get('userID') == getCUserData().get('_id'):
                        Quote.updateQuoteData(quote=quote_,
                                              quoteID=quoteID)
                        GenImage(quote=quote_,
                         author=getCUserData().get('name').upper(),
                                 quoteID = qobj.get('quoteID'), update_=True)

                        # flash('Press SHIFT + F5 key to see the changes')
                        return jsonify({'success': True})
                    else:
                        return jsonify({'error': 'invalid user'})

                elif request.method == 'DELETE':
                    quoteID = data.get('quoteID')
                    qobj = User.getQuotebyQuoteID(quoteID)
                    if qobj.get('userID') == getCUserData().get('_id'):
                        Quote.removeByQuoteID(quoteID)
                        flash('Quote Deleted Successfully!')
                        return jsonify({'success': True})
                    else:
                        return jsonify({'error': 'invalid user'})

            if data.get('fieldType', '') == 'username':
                usr = getCUserData()
                if usr:
                    uname = data.get('data')
                    if len(uname) > 100:
                        flash('Username too Long!')
                        return jsonify({'error': 'failed'})

                    if not uname.replace('_', '').isalnum():
                        flash('Username Must Not Contain Special Characters')
                        return jsonify({'error': 'failed'})

                    uname = uname.replace(' ', '_')
                    result = User.changeUsername(
                        usr.get('_id'), uname)
                    # print(result)
                    flash('Username Changed Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            elif data.get('fieldType', '') == 'about':
                usr = getCUserData()
                if usr:
                    about = data.get('data')
                    about = about.replace('\n', '<br>')
                    result = User.changeAbout(usr.get('_id'),
                                              about)
                    # print(result)
                    flash('About You updated Successfully Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            elif data.get('fieldType', '') == 'password':
                usr = getCUserData()
                if usr:
                    result = User.changePassword(
                        usr.get('_id'), data.get('data'))
                    print(result)
                    flash('Password Changed Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            elif data.get('fieldType', '') == 'email':
                usr = getCUserData()
                if usr:
                    result = User.changeEmail(
                        usr.get('_id'), data.get('data'))
                    print(result)
                    flash('Email Address Changed Successfully!')
                else:
                    flash('Please Login to Make these Changes..')
                    return redirect('/', 302)

            else:
                return(jsonify({'success': False}))

            if result:
                return(jsonify({'success': True}))
            else:
                return(jsonify({'success': False}))

        else:
            print('data not found')
            return redirect('/')
    else:
        print('invalid request')
        return('<h1>Invalid Request Sent to The Server</h1>', 404)


@app.route("/submit/quote", methods=['GET', 'POST'])
def upload():
    if User.sessionCreatedAt(session.get('_cu', None)):
        form = UploadForm()
        if request.method == 'POST':
            if form.validate() == False:
                flash('Validation Failed!')
                return redirect(url_for('upload'))
            else:
                # print(Keywords(fileObj))
                quote_id = str(uuid4().hex)[::-1]
                User.PostQuote(session.get('_cu'),
                               quote=form.quote.data,
                               quoteID=quote_id)
                return redirect(f'/quotes/{quote_id}', 302)

        elif request.method == 'GET':
            return render_template('upload.html', form=form)

    else:
        if session.get('_cu'):
            flash('Please Login to Post a Quote..')
            session.pop('_cu', None)
        else:
            flash('Please Login to Post a Quote!')
        return redirect(url_for('login'))


@app.route("/about")
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
