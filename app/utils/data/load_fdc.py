from deep_translator import GoogleTranslator
from flask import current_app

from app.utils.update_models import update_ingredient, update_nutrition, update_nutriConversion, update_conversion
from app.utils.data import TO_SCRAPE, file_reader
from app.utils import convert_to_float
from app.utils.dicts import NUTRITION_IDS, MEASURE_UNITS, STD_ENERGY_CONVERSION

#--------------------

def fdc_from_csv(food_path: str = None, conversion_path: str = None, conversion_index_path: str = None, nutrient_path: str = None, portion_path: str = None) -> None:
    """
    This function loads the data from the FDC database into the database from 5 csv files provided by the user.

    Arguments:
    food_path (str): The path to the csv file containing the foods.
    conversion_path (str): The path to the csv file containing the conversions for energy calculation.
    conversion_index_path (str): The path to the csv file containing the conversion index for energy calculation.
    nutrient_path (str): The path to the csv file containing the nutrients.
    portion_path (str): The path to the csv file containing the portions.

    Returns:
    None

    Raise:
    None
    """
    # Add all foods available in the database to the Ingredients table
    if food_path:
        __store_ingredients(food_path)

    # Update the NutriConversion Table with only elements that are in the Ingredient table
    if conversion_path and conversion_index_path:
        __store_nutriConversion(conversion_path, conversion_index_path)

    # Update the Nutrition table with only the elements which are present in the Ingredients table
    if nutrient_path:
        __store_nutrition(nutrient_path)

    # Update the Conversion table with only the elements which are present in the Ingredients table
    if portion_path:
        __store_conversion(portion_path)


def __store_ingredients(food_path: str) -> None:
    """
    This function adds all foods available (specific groups only) in the database to the Ingredients table.

    Arguments:
    food_path (str): The path to the csv file containing the foods.

    Returns:
    None

    Raises:
    None
    """
    # Itterate over rows where data_type is set to scrape and store the data in the ingredient database
    for row in file_reader(food_path):
        if row['data_type'] in TO_SCRAPE:
            # Extract data from the row
            name_en = row['description']
            name_nl = GoogleTranslator(source='en', target='nl').translate(name_en)
            fdc_id = row['fdc_id']
            synonyms = [] # Not in file, so standard value
            unit = 'g' # Not in file, so standard value
            
            # Store the ingredient object in the database
            update_ingredient(
                name_nl = name_nl,
                name_en = name_en, 
                fdc_id = fdc_id,
                synonyms = synonyms,
                unit = unit
                )


def __store_nutriConversion(conversion_path: str, conversion_index_path: str) -> None:
    """
    This function updates the NutriConversion Table with only elements that are in the Ingredient table.

    Arguments:
    conversion_path (str): The path to the csv file containing the nutrient conversion factors.
    conversion_index_path (str): The path to the csv file containing the index of the nutrient conversion factors.

    Returns:
    None

    Raises:
    None
    """
    # Itterate over rows and store standardized conversions with the links to the Ingredient table
    for row in file_reader(conversion_index_path):
        fdc_id = row['fdc_id']
        conversion_id = row['id']

        # Store the link information in the databasewith standardized values
        update_nutriConversion(
            fdc_id = fdc_id,
            conversion_id = conversion_id,
            protein_value = STD_ENERGY_CONVERSION['PROTEIN'],
            fat_value = STD_ENERGY_CONVERSION['FAT'],
            carb_value = STD_ENERGY_CONVERSION['CARBS']
            )

    # Itterate over rows to store the ingredient-specific conversion factors
    for row in file_reader(conversion_path):
        conversion_id = row['food_nutrient_conversion_factor_id']
        protein_value = convert_to_float(row['protein_value']) if row['protein_value'] else STD_ENERGY_CONVERSION['PROTEIN']
        fat_value = convert_to_float(row['fat_value']) if row['fat_value'] else STD_ENERGY_CONVERSION['FAT']
        carb_value = convert_to_float(row['carbohydrate_value']) if row['carbohydrate_value'] else STD_ENERGY_CONVERSION['CARBS']

        # Store the ingredient-specific conversion factors in the database
        update_nutriConversion(
            conversion_id = conversion_id,
            protein_value = protein_value,
            fat_value = fat_value,
            carb_value = carb_value
            )


def __store_nutrition(nutrient_path: str) -> None:
    """
    This function is used to parse the nutrients.csv file and store the data in the database.

    Arguments:
    nutrient_path (str): The path to the nutrients.csv file.

    Returns:
    None

    Raises:
    None
    """
    # Itterate over rows where fdc_id is stored already and store the corresponding data in the nutrition database
    for row in file_reader(nutrient_path):
        # Extract data
        fdc_id = row['fdc_id']
        amount = convert_to_float(row['amount']) if row['amount'] else 0.0
        nutrient_id = row['nutrient_id']

        try:
            nutrient_name = NUTRITION_IDS[int(nutrient_id)]
        except:
            # Pass this nutrition as it is not relevent
            continue

        # Update nutrition object
        match nutrient_name:
            case 'Protein (N x 6.25) Dumas':
                update_nutrition(
                    fdc_id = fdc_id,
                    protein = amount
                )
            case 'Fat-Soxhlet':
                update_nutrition(
                    fdc_id = fdc_id,
                    fat = amount
                )
            case 'Total SFA':
                update_nutrition(
                    fdc_id = fdc_id,
                    saturated = amount
                )
            case 'Total Carbohydrates':
                update_nutrition(
                    fdc_id = fdc_id,
                    carbs = amount
                )
            case 'TOTAL SUGAR':
                update_nutrition(
                    fdc_id = fdc_id,
                    sugar = amount
                )
            case 'Na':
                update_nutrition(
                    fdc_id = fdc_id,
                    salt = amount / 1000
                )
            case _:
                # Head to next row in the csv file
                continue


def __store_conversion(portion_path: str) -> None:
    """
    This function is used to parse and store the portion information from the csv file into the database.

    Arguments:
    portion_path (str): The path to the portion csv file.

    Returns:
    None

    Raises:
    NutritionInvalid: When the nutrition info is invalid.
    NutritionAlreadyExists: When the nutrition info already exists.
    Exception: When an unknown error occurs.
    """
    # Itterate over rows where fdc_id is stored already and store the corresponding data in the Conversion database
    for row in file_reader(portion_path):
        fdc_id = row['fdc_id']
        amount = convert_to_float(row['amount']) if row['amount'] else 0.0
        measure_unit_id = row['measure_unit_id'] if row['measure_unit_id'] else None
        description = row['portion_description'] if row['portion_description'] else None
        modifier = row['modifier'] if row['modifier'] else None
        gram_weight = convert_to_float(row['gram_weight']) if row['gram_weight'] else 0.0

        measure_unit = MEASURE_UNITS[int(measure_unit_id)] if MEASURE_UNITS[int(measure_unit_id)] else None
        unit = " ".join([elem for elem in [measure_unit, description, modifier] if elem]) if (measure_unit or description or modifier) else ""

        current_app.logger.debug(f"fdc_id: {fdc_id}, amount: {amount}, unit: {unit}, value: {gram_weight}")

        # Update the conversion object
        update_conversion(
            fdc_id = fdc_id,
            amount = amount,
            unit = unit,
            value = gram_weight
        )


                