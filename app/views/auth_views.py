from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_user, logout_user, current_user

from app import db, lm
from app.forms import LoginForm, CreateAccountForm
from app.models import User
from app.utils.authentication import verify_pass

#--------------------

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # Read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            current_app.logger.debug(f'User {user.username} logged in')
            
            return redirect(url_for('main.home'))
        
        # Something (user or password) is not ok
        flash('Gebruikersnaam of wachtwoord is onjuist', "error")
        logout_user()
        return render_template('accounts/login.html', form=login_form)
    
    if not current_user.is_authenticated:
        return render_template('accounts/login.html', form=login_form)
    
    return redirect(url_for('main.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        username = request.form['username']
        email = request.form['email']

        # Check username exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Deze gebruikersnaam bestaat al', "error")
            return render_template('accounts/register.html', success=False, form=create_account_form)
        
        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Dit e-mailadres is al in gebruik', "error")
            return render_template('accounts/register.html', success=False, form=create_account_form)
        
        # Else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()

        current_app.logger.info(f'New user {user.username} registered')

        flash('Account aangemaakt','success')
        return render_template('accounts/register.html', success=True, form=create_account_form)
    
    else:
        return render_template('accounts/register.html', form=create_account_form)

@auth.route('/logout')
def logout():
    current_app.logger.debug(f'User {current_user.username} logged out')
    logout_user()
    return redirect(url_for('auth.login'))

# Errors
@lm.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@auth.errorhandler(403)
def access_forbidden():
    return render_template('home/page-403.html'), 403


@auth.errorhandler(404)
def not_found_error():
    return render_template('home/page-404.html'), 404


@auth.errorhandler(500)
def internal_error():
    return render_template('home/page-500.html'), 500