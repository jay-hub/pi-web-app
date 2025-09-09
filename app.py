import uuid

from flask import Flask, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/user_data.db'
app.config['SECURITY_PASSWORD_SALT'] = 'some_salt'

db = SQLAlchemy(app)


@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()

    seed_user = User(
        name="Admin User",
        email="admin@gmail.com",
        password="admin",
        is_admin=True
    )
    if not User.query.filter_by(email=seed_user.email).first():
        db.session.add(seed_user)
        db.session.commit()


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')


class User(db.Model):
    __tableName__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    last_login_at = db.Column(db.DateTime(), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True)

    def __init__(self, name, email, password, active=True, is_admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.is_admin = is_admin


@app.route('/')
def home():
    users = User.query.all()
    message = f"Total users: {len(users)}"
    return f"Hello, World! {message}"


@app.route('/login')
def login():
    return "Login Page"


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
