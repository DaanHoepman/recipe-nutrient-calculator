import os
import hashlib
import binascii

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

#--------------------

def hash_pass(password: str) -> str:
    """
    This function hashes a password using a salt and pbkdf2_hmac

    Arguments:
    password (str): The password to be hashed

    Returns:
    str: The hashed password

    Raises:
    Exception: If the password is None or empty
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)

    return (salt + pwdhash)

def verify_pass(provided_password: str, stored_password: str) -> bool:
    """
    This function verifies a password by comparing the hashed password with the stored password

    Arguments:
    provided_password (str): The password provided by the user
    stored_password (str): The hashed password stored in the database

    Returns:
    bool: True if the passwords match, False otherwise

    Raises:
    Exception: If the provided password is None or empty
    Exception: If the stored password is None or empty
    """
    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')

    return pwdhash == stored_password

def admin_required(f):
    """
    This function checks if the user is an admin and if not, redirects them to the homepage

    Arguments:
    f: The function to be decorated

    Returns:
    The decorated function

    Raises:
    Exception: If the user is not authenticated
    Exception: If the user is not an admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Je moet ingelogd zijn om deze pagina te kunnen bekijken.', 'danger')
            return redirect(url_for('auth.login'))
        
        elif not current_user.is_admin:
            flash('Je hebt geen toestemming om deze pagina te bekijken', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function