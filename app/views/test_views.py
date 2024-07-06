from flask import Blueprint, render_template, abort
#--------------------

test = Blueprint('test', __name__)

@test.route('/trigger-403')
def trigger_403():
    abort(403)

@test.route('/trigger-404')
def trigger_404():
    abort(404)

@test.route('/trigger-500')
def trigger_500():
    abort(500)