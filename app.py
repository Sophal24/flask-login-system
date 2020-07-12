import os
import requests
from flask import Flask, render_template, redirect, url_for, flash, session,request, flash, jsonify
from flask import send_file # help to download file, 
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO # help to downlaod file
from pocketsphinx import AudioFile
import base64


from base64 import b64encode

from pocketsphinx import AudioFile


from base64 import b64encode

from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/Volumes/HDD/WEB/Flask/building_user_login_system/finish/static/sound'
ALLOWED_EXTENSIONS = {'wav','mp3'}
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav','mp3'}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:24071999@localhost/prettyprinted' #posgresql+username+password=@localhost/database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vqfhxxncclgtkm:87c1e6539b84ba12105a17cfc6733cb2ddb9d7b902c896ca73791f6c9ab17f2d@ec2-3-91-139-25.compute-1.amazonaws.com:5432/d6mglfsgk46cmg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Validator of Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

# Validator of Signup Form
class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    password_confirm = PasswordField('Confirm password*', validators=[InputRequired(), EqualTo('password')])




# Model for Lexicon
class Lexicon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), unique=True)
    pronounciation = db.Column(db.String(100), unique=True)
    utteranceid = db.Column(db.String(100), unique=True)

    def __init__(self, word, pronounciation, utteranceid):
        self.word = word
        self.pronounciation = pronounciation
        self.utteranceid = utteranceid

# ===============CRUD Lexicon===============
# Add Lexicon
@app.route('/insertlexicon', methods=['POST'])
@login_required
def insertlexicon():
    word = request.form['word']
    pronounciation = request.form['pronounciation']
    utteranceid = request.form['utteranceid']
    lexicon = Lexicon(word,pronounciation,utteranceid)

    exist1 = Lexicon.query.filter_by(word=word).first()
    exist2 = Lexicon.query.filter_by(pronounciation=pronounciation).first()
    exist3 = Lexicon.query.filter_by(utteranceid=utteranceid).first()
    
    if exist1 or exist2 or exist3:
        flash("This lexicon already exists!", "warning")
        return redirect(url_for('lexicon'))

    db.session.add(lexicon)
    db.session.commit()
    flash("New Lexicon has just been added successfully.", "success")
    return redirect(url_for('lexicon'))

# Update Lexicon
@app.route('/updatelexicon', methods=['Get', 'POST'])
@login_required
def updatelexicon():
    if request.method == 'POST':
        update = Lexicon.query.get(request.form.get('id'))
        
        update.word = request.form['word']
        update.pronounciation = request.form['pronounciation']
        update.utteranceid = request.form['utteranceid']

        db.session.commit()
        flash("Lexicon was updated successfully !!!", "success")
        return redirect(url_for('lexicon'))
    else:
        flash("Failed to update Lexicon !!!", "warning")
        return redirect(url_for('lexicon'))

# Delete a Lexicon
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    lexiconDelete = Lexicon.query.get_or_404(id)
    try:
        db.session.delete(lexiconDelete)
        db.session.commit()
        flash("Lexicon was deleted successfully !!!","success")
        return redirect(url_for('lexicon'))
    except:
        flash("There was a problem delete lexicon !!!","warning")
        return redirect(url_for('lexicon'))

# ===============x End CRUD Lexicon x===============





# Model for Language Model Management
class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String, unique=True)
    pronounciation = db.Column(db.String, unique=True)
    
    def __init__(self, word, pronounciation):
        self.word = word
        self.pronounciation = pronounciation

# ================ CRUD on LMM ===================
@app.route('/insertlanguage', methods=["POST"])
@login_required
def insertlanguage():
    word = request.form['word']
    pronounciation = request.form['pronounciation']

    language = Language(word,pronounciation)

    exist1 = Language.query.filter_by(word=word).first()
    exist2 = Language.query.filter_by(pronounciation=pronounciation).first()
    
    if exist1 or exist2:
        flash("This Language already exists!", "warning")
        return redirect(url_for('language'))

    db.session.add(language)
    db.session.commit()
    flash("New Word has just been added successfully.", "success")
    return redirect(url_for('language'))



# Update Lexicon
@app.route('/updatelang', methods=['Get', 'POST'])
@login_required
def updatelang():
    if request.method == 'POST':
        updatelang = Language.query.get(request.form.get('id'))
        
        updatelang.word = request.form['word']
        updatelang.pronounciation = request.form['pronounciation']

        db.session.commit()
        flash("Word was updated successfully !!!", "success")
        return redirect(url_for('language'))
    else:
        flash("Failed to update Lexicon !!!", "warning")
        return redirect(url_for('language'))


# Delete a Language Model
@app.route('/deletelang/<int:id>')
@login_required
def deletelang(id):
    langDelete = Language.query.get_or_404(id)
    try:
        db.session.delete(langDelete)
        db.session.commit()
        flash("New word was deleted successfully !!!", "success")
        return redirect(url_for('language'))
    except:
        flash("There was a problem delete word !!!", "warning")
        return redirect(url_for('language'))

# ================x End CRUD on LMM x================


class VoiceFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)
        
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

# ================ Speech management =================
# function to upload voice file (upload into database)
@app.route('/uploadvoice', methods=["POST"])
@login_required
def uploadvoice():
    file = request.files['inputFile']

    if file and allowed_file(file.filename):
        newFile = VoiceFile(filename=file.filename, data=file.read())
        db.session.add(newFile)
        db.session.commit()

        flash("File Saved Successfully.","success")
        return redirect(url_for('speech'))
    else:
        flash("File Extesion is not allowed. (.wav and .mp3 only!)", "danger")
        return redirect(url_for('speech'))

    # newFile = VoiceFile(filename=file.filename, data=file.read())
    # db.session.add(newFile)
    # db.session.commit()

    # flash("File Saved Successfully.","success")
    # return redirect(url_for('speech'))


# Check File extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

<<<<<<< HEAD
# Function Delete file from database.
@app.route('/voicedelete/<int:id>')
@login_required
def voicedelete(id):
    voiceDelete = VoiceFile.query.get_or_404(id)
    try:
        db.session.delete(voiceDelete)
        db.session.commit()
        flash("Voice was deleted successfully !!!","success")
        return redirect(url_for('speech'))
    except:
        flash("There was a problem delete lexicon !!!","warning")
        return redirect(url_for('speech'))
=======
>>>>>>> e66097cf2560a757d7a45898615c6fbdac1a027f

# function to upload file into a folder 
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file', filename=filename))

            flash("File saved successfully", "success")
            return redirect(url_for('speech'))
        else:
            flash("File Extesion is not allowed.", "danger")
            return redirect(url_for('speech'))

## upload voice API (into folder)
@app.route('/uploadapi', methods=['POST'])
def uploadapi():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify(message="No file part", statusMessage="No Content", staus="204"), 204
        file = request.files['file']

        
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify(message="No selected File.", statusMessage="Error", status="404"), 404

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file', filename=filename))
<<<<<<< HEAD
            # config = {
            #     'verbose' : False,
            #     'logfn' : '/dev/null' or 'nul',
            #     'audio_file' : 'tovmok.wav',
            #     'audio_device' : None,
            #     'sampling_rate' : 16000,
            #     'buffer_size' : 2048,
            #     'no_search' : False,
            #     'full_utt' : False,
            #     'hmm' : 'ASRProject/model_parameters/iot.ci_cont',
            #     'lm' : 'ASRProject/etc/iot.lm.DMP',
            #     'dict' : 'ASRProject/etc/iot.dic',
            # }

            # audio = AudioFile(**config)
            # for phrase in audio:
            #     word = phrase
            #     pass

            return jsonify(message="File Saved Successfully.",result="ទៅមុខ", statusMessage="Success", status="200"), 200
=======
            config = {
                'verbose' : False,
                'logfn' : '/dev/null' or 'nul',
                'audio_file' : 'tovmok.wav',
                'audio_device' : None,
                'sampling_rate' : 16000,
                'buffer_size' : 2048,
                'no_search' : False,
                'full_utt' : False,
                'hmm' : 'ASRProject/model_parameters/iot.ci_cont',
                'lm' : 'ASRProject/etc/iot.lm.DMP',
                'dict' : 'ASRProject/etc/iot.dic',
            }

            audio = AudioFile(**config)
            for phrase in audio:
                word = phrase
                pass

            return jsonify(message="File Saved Successfully.",result=word, status="200"), 200
>>>>>>> e66097cf2560a757d7a45898615c6fbdac1a027f

        else:
            return jsonify(message="File Extesion is not allowed.", statusMessage="Error", status="404"), 404


# decode voice file into khmer text
@app.route('/phone')
def phone():
    config = {
        'verbose' : False,
        'logfn' : '/dev/null' or 'nul',
        'audio_file' : 'tovmok.wav',
        'audio_device' : None,
        'sampling_rate' : 16000,
        'buffer_size' : 2048,
        'no_search' : False,
        'full_utt' : False,
        'hmm' : 'ASRProject/model_parameters/iot.ci_cont',
        'lm' : 'ASRProject/etc/iot.lm.DMP',
        'dict' : 'ASRProject/etc/iot.dic',
    }

    audio = AudioFile(**config)
    for phrase in audio:
        print(phrase)


# decode voice file into khmer text
@app.route('/phone')
def phone():
    config = {
        'verbose' : False,
        'logfn' : '/dev/null' or 'nul',
        'audio_file' : 'tovmok.wav',
        'audio_device' : None,
        'sampling_rate' : 16000,
        'buffer_size' : 2048,
        'no_search' : False,
        'full_utt' : False,
        'hmm' : 'ASRProject/model_parameters/iot.ci_cont',
        'lm' : 'ASRProject/etc/iot.lm.DMP',
        'dict' : 'ASRProject/etc/iot.dic',
    }

    audio = AudioFile(**config)
    for phrase in audio:
        print(phrase)


# ==============xEnd Speech management x==============



@app.route('/')
@app.route('/index')
# @login_required
def index():
    return render_template('index.html', home=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # return current_app.login_manager.unauthorized()
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

<<<<<<< HEAD
        flash("Invalid Username or Password.","danger")
=======
        return '<h1>Invalid username or password</h1>'
>>>>>>> e66097cf2560a757d7a45898615c6fbdac1a027f

    return render_template('login.html', form=form, login=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        # return current_app.login_manager.unauthorized()
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        user = User.query.filter_by(username=username).first()
        uemail = User.query.filter_by(email=email).first()

        if user and uemail:
            flash("Username and Email already exist. Please Try Again!","warning")
            return redirect(url_for('signup'))
        elif user:
            flash("Username already exist. Please Try Again!","warning")
            return redirect(url_for('signup'))
        elif uemail:
            flash("Email already exist. Please Try Again!","warning")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(form.password.data, method='sha256') #hash password
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password) #put all data from form in to Class User
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form, signup=True)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username, dashboard=True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    # session.pop('login', None)
    return redirect(url_for('index'))



@app.route('/lexicon')
@login_required
def lexicon():
    # lexiconall = Lexicon.query.all()
    lexiconall = Lexicon.query.order_by(Lexicon.id.asc()).all()
    count = Lexicon.query.count()
    return render_template('lexicon.html', lexicon=True, lexiconall=lexiconall, count=count)


@app.route('/language')
@login_required
def language():
    # languageall = Language.query.all()
    languageall = Language.query.order_by(Language.id.asc()).all()
    count = Language.query.count()
    return render_template('language.html', language=True, languageall=languageall, count=count)


@app.route('/speech')
@login_required
def speech():
    # voice = VoiceFile.query.all()
    voice = VoiceFile.query.all()
<<<<<<< HEAD
    count = VoiceFile.query.count()
    return render_template('speech.html', speech=True, voice=voice, count=count)
=======
    return render_template('speech.html', speech=True, voice=voice)
>>>>>>> e66097cf2560a757d7a45898615c6fbdac1a027f


@app.route('/decoding')
@login_required
def decoding():
    return render_template('decoding.html', decoding=True)



@app.route("/show/<int:id>")
def show(id):
    obj = VoiceFile.query.get_or_404(id)
    image = b64encode(obj.data).decode("utf-8")
    return render_template("speech.html", obj=obj, image=image)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
