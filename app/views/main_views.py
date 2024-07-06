import os
import logging

from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from app.utils.data.load_nevo import from_csv
from app.utils.data.load_fdc import fdc_from_csv
from app.utils.data import allowed_file
from app.utils.authentication import admin_required

#--------------------

main = Blueprint('main', __name__)

# Global site variables to be used in templates
@main.context_processor
def inject_now():
    return {'current_year': datetime.now().year,
            'app_fix': 'DH',
            'app_name': 'Daan Hoepman',
            'current_user': current_user,
            }

# Home landing page
@main.route('/')
def home():
    return render_template('home/home.html')

# Route for updating the NEVO database by uploading a CSV file
@main.route('/update_nevo', methods=['GET', 'POST'])
@admin_required
def update_nevo():
    if request.method == 'POST':
        # Check if the file part is in the request
        if 'file' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)
        
        # Check if the file has a filename
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)
        
        # Check if the file is allowed (CSV format)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # Save the uploaded file
            file.save(filepath)
            current_app.logger.info(f'File {filepath} uploaded by user {current_user.username}')

            # Process the CSV file and store data in the database
            from_csv(filepath)

            flash('File successfully uploaded and processed', category='success')
            current_app.logger.info(f'NEVO database succesfully updated by user {current_user.username}')

            return redirect(url_for('main.update_nevo'))

    return render_template('home/update_nevo.html')

# Route for updating the FoodData Central database by uploading multiple CSV files
@main.route('/update_fdc', methods=['GET', 'POST'])
@admin_required
def update_fdc():
    if request.method == 'POST':
        # Initialize a None-filled dictionary to collect file paths
        res_files = {'food': None, 'food_calorie_conversion_factor': None, 'food_nutrient_conversion_factor': None, 'food_nutrient': None, 'food_portion': None}
        files = request.files.getlist("files")

        acc_files = [file.filename for file in files if file.filename[:-4] in res_files]
        if not acc_files:
            flash("All files provided are not required", category='error')
            return redirect(request.url)

        for file in files:            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                # Save the uploaded file
                file.save(filepath)
                current_app.logger.info(f'File {filepath} uploaded by user {current_user.username}')

                # Add file path to the dict
                res_files[file.filename[:-4]] = filepath
                current_app.logger.debug(f'File {file.filename[:-4]} added to the upload dict')

        # Pass all stored files to the processing function
        fdc_from_csv(
            res_files['food'], 
            res_files['food_calorie_conversion_factor'], 
            res_files['food_nutrient_conversion_factor'], 
            res_files['food_nutrient'], 
            res_files['food_portion']
            )

        flash('Files successfully uploaded and processed', category='success')
        current_app.logger.info(f'FoodData Central database succesfully updated by user {current_user.username}')

        return redirect(url_for('main.update_fdc'))
    
    return render_template('home/update_fdc.html')