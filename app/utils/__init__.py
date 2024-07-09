from sqlalchemy.exc import IntegrityError
from flask import current_app

from app.models import Ingredient, Nutrition, NutriConversion
from app.utils.exceptions import ElementNotFound, DatabaseError
from app.utils.dicts import STD_ENERGY_CONVERSION
from app import db

#--------------------

def convert_to_float(value) -> float:
    """
    This function converts the given value to a float, regardless of the decimal seperator

    Arguments:
    value (str):  The value to be converted to a float

    Returns:
    float:  The converted value

    Raises:
    None
    """
    try:
        # Replace comma with dot and convert to float
        return float(value.replace(',', '.'))
    except ValueError:
        # If conversion fails return the original value (already a float)
        return value
    

def calculate_energy(ingredient: Ingredient) -> tuple[float, float]:
    """
    This function calculates the energy values of the given ingredient.

    Arguments:
    ingredient (Ingredient):  The ingredient to calculate the energy values for

    Returns:
    tuple[float, float]:  A tuple containing the energy values in kCal and kJ

    Raises:
    ElementNotFound:  If the ingredient could not be found in the database
    """
    # Query the NutriConversion values from the database
    ingredient_id = ingredient.id
    conversion = db.session.query(NutriConversion).filter_by(ingredient_id=ingredient_id).first()
    nutrition = db.session.query(Nutrition).filter_by(ingredient_id=ingredient_id).first()
    
    if not nutrition:
        raise ElementNotFound(f"Could not find Nutrition information for Ingredient: {ingredient.name_en}")
    
    if not conversion:
        # Use standard value
        energy_kcal = sum([
            nutrition.carbs * STD_ENERGY_CONVERSION['CARBS'],
            nutrition.protein * STD_ENERGY_CONVERSION['PROTEIN'],
            nutrition.fat * STD_ENERGY_CONVERSION['FAT']
        ])
    else:
        # Use ingredient-specific value
        energy_kcal = sum([
            nutrition.carbs * conversion.carb_value,
            nutrition.protein * conversion.protein_value,
            nutrition.fat * conversion.fat_value
        ])

    energy_kj = energy_kcal * STD_ENERGY_CONVERSION['KJ_TO_KCAL']

    return (energy_kcal, energy_kj)


def try_commit(error_id) -> None:
    """
    This function tries to commit the changes to the database. If the commit fails, the changes are rolled back.

    Arguments:
    error_id (int):  The id of the element that caused the error

    Returns:
    None

    Raises:
    Exception:  If the commit fails
    """
    try:
        current_app.logger.debug("Committing changes to database...")
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise DatabaseError(f"Could not commit changes to database for id: {str(error_id)}")