import json

from app.utils import convert_to_float
from app.utils.data import file_reader
from app.utils.update_models import update_ingredient, update_nutrition

#--------------------

def from_csv(path: str) -> None:
    """
    This function reads a csv file and stores the data in the database.

    Arguments:
        path (str): The path to the csv file.

    Returns:
        None

    Raises:
        None
    """
    # Itterate over all rows and store the data in the ingredient database and store information
    for row in file_reader(path, '|'):
        # Extract data from the row
        name_nl = row['Voedingsmiddelnaam/Dutch food name']
        name_en = row['Engelse naam/Food name']
        nevo_id = int(row['NEVO-code'])
        synonyms = row['Synoniem'].split('/') if row['Synoniem'] else []
        unit = row['Hoeveelheid/Quantity'][7:]
        energy_kj = convert_to_float(row['ENERCJ (kJ)']) if row['ENERCJ (kJ)'] else 0.0
        energy_kcal = convert_to_float(row['ENERCC (kcal)']) if row['ENERCC (kcal)'] else 0.0
        protein = convert_to_float(row['PROT (g)']) if row['PROT (g)'] else 0.0
        fat = convert_to_float(row['FAT (g)']) if row['FAT (g)'] else 0.0
        saturated = convert_to_float(row['FASAT (g)']) if row['FASAT (g)'] else 0.0
        carbs = convert_to_float(row['CHO (g)']) if row['CHO (g)'] else 0.0
        sugar = convert_to_float(row['SUGAR (g)']) if row['SUGAR (g)'] else 0.0
        salt = (convert_to_float(row['NA (mg)']) / 1000) if row['NA (mg)'] else 0.0
            
        # Add the ingredient object to the database and store ingredient object in memory
        ingredient = update_ingredient(
            name_nl = name_nl,
            name_en = name_en,
            nevo_id = nevo_id,
            synonyms = synonyms,
            unit = unit
        )
    
        # Add the ingredient object to the database
        update_nutrition(
            ingredient_id = ingredient.id,
            energy_kj = energy_kj,
            energy_kcal = energy_kcal,
            protein = protein,
            fat = fat,
            saturated = saturated,
            carbs = carbs,
            sugar = sugar,
            salt = salt
        )