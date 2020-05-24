from flask import Flask, render_template, redirect, url_for, flash, session,request, flash
# from flask_bootstrap import Bootstrap
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:24071999@localhost/prettyprinted'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vqfhxxncclgtkm:87c1e6539b84ba12105a17cfc6733cb2ddb9d7b902c896ca73791f6c9ab17f2d@ec2-3-91-139-25.compute-1.amazonaws.com:5432/d6mglfsgk46cmg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

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

# Validator of Login and Signup Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

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
    pronounciation = request.form['prounounciation']
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
        update.pronunciation = request.form['pronounciation']
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

# ===============End CRUD Lexicon===============


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

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form, login=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        # return current_app.login_manager.unauthorized()
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256') #hash password
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password) #put all data from form in to Class User
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('dashboard'))
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
    lexiconall = Lexicon.query.all()
    count = Lexicon.query.count()
    return render_template('lexicon.html', lexicon=True, lexiconall=lexiconall, count=count)

@app.route('/language')
@login_required
def language():
    return render_template('language.html', language=True)

@app.route('/speech')
@login_required
def speech():
    return render_template('speech.html', speech=True)

@app.route('/decoding')
@login_required
def decoding():
    return render_template('decoding.html', decoding=True)


# @app.route('/base')
# @login_required
# def base():
#     return render_template('base.html', decoding=True)



if __name__ == '__main__':
    app.run(debug=True)
