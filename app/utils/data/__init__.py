import os
import csv

from app.config import Config

#--------------------

# Load food-data central variables
FDC_API_KEY = Config().FDC_API_KEY
FDC_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search?"
FDC_MATCH_URL = "https://api.nal.usda.gov/fdc/v1/food"
FDC_BULK_MATCH_URL = "https://api.nal.usda.gov/fdc/v1/foods?"

TO_SCRAPE = ['sr_legacy_food', 'foundation_food']


# Load NEVO variables
NEVO_HEADERS = [
    'NEVO-code',
    'Voedingsmiddelnaam/Dutch food name',
    'Engelse naam/Food name',
    'Synoniem',
    'Hoeveelheid/Quantity',
    'ENERCJ (kJ)',
    'ENERCC (kcal)',
    'PROT (g)',
    'FAT (g)',
    'FASAT (g)',
    'CHO (g)',
    'SUGAR (g)',
    'NA (mg)',
]


def allowed_file(filename: str) -> bool:
    """
    This function checks if the file is a csv file.

    Arguments:
        filename (str): The filename of the file.

    Returns:
        bool: True if the file is a csv file, otherwise False.

    Raises:
        ValueError: If the filename is not a string.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


def file_reader(file_path: str, delimiter: str = ','):
    """
    This function reads a csv file and yields the rows.

    Arguments:
        file_path (str): The path to the csv file.
        delimiter (str): The delimiter of the csv file.

    Returns:
            Iterator[Dict[str, str]]: The rows of the csv file.	

    Raises:
            Exception: If the file could not be read.
    """
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            # Read the csv file
            reader = csv.DictReader(file, delimiter=delimiter)
            for row in reader:
                yield row
    except Exception as e:
        raise Exception(f"Error reading file: {e}")