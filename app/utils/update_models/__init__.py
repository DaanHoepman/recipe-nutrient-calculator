import json

from flask import current_app

from app import db
from app.utils import calculate_energy, try_commit
from app.models import Ingredient, Conversion, Nutrition, NutriConversion
from app.utils.exceptions import ElementNotFound, ElementInvalid

#--------------------

def update_ingredient(name_nl: str = None, name_en: str = None, nevo_id: int = None, fdc_id: int = None, synonyms: list = None, unit: str = None) -> Ingredient:
    """
    This function updates an Ingredient object in the database from either the nevo_id or fdc_id

    Arguments:
    name_nl (str): the name of the food in dutch, standard value is None
    name_en (str): the name of the food in english, standard value is None
    nevo_id (int): the id as available in the NEVO database, standard value is None
    fdc_id (int): the id as available in the FoodData Central database, standard value is None
    synonyms (list): list of different names used for the same ingredient, standard value is None
    unit (str): specifying the unit for amount of nutrition per unit (eg: per 100g), standard value is None

    Returns:
    The updated Ingredient object

    Raises:
    IngredientInvalid: Ingredient could not be parsed
    IngredientAlreadyExists: Ingredient already exists in the database
    """
    try:
        # Check if the ingredient already exists in the database
        if nevo_id is not None:
            existing_ingredient = db.session.query(Ingredient).filter_by(nevo_id=nevo_id).first()
        elif fdc_id is not None:
            existing_ingredient = db.session.query(Ingredient).filter_by(fdc_id=fdc_id).first()
        else:
            raise Exception("Nevo ID or FDC ID must be provided")

        if existing_ingredient:
            current_app.logger.debug(f"Updating existing ingredient {existing_ingredient.id}")
            # Update existing ingredient
            if name_nl is not None:
                existing_ingredient.name_nl = name_nl
            if name_en is not None:
                existing_ingredient.name_en = name_en
            if synonyms is not None:
                existing_ingredient.synonyms = json.dumps(synonyms)
            if unit is not None:
                existing_ingredient.unit = unit

            new_object = existing_ingredient
        else:
            current_app.logger.debug(f"Creating new ingredient with name_en: {name_en} and name_nl: {name_nl} and nevo_id: {nevo_id} and fdc_id: {fdc_id} and synonyms: {synonyms} and unit: {unit}")

            # Create new ingredient
            ingredient = Ingredient(
                name_nl = name_nl,
                name_en = name_en,
                nevo_id = nevo_id,
                fdc_id = fdc_id,
                synonyms = json.dumps(synonyms),
                unit = unit
            )

            db.session.add(ingredient)
            new_object = ingredient

        # Try to commit the transaction
        try_commit(name_en if name_en else name_nl)

        current_app.logger.debug(f"Successfully updated ingredient {new_object.id}")
        
    except Exception as e:
        db.session.rollback()
        raise ElementInvalid(f"Ingredient could not be parsed: {str(e)}")
    finally:
        return new_object



def update_conversion(fdc_id: int = None, ingredient_id: int = None, amount: float = None, unit: str = None, value: float = None) -> Conversion:
    """
    This function updates a Conversion object in the database

    Arguments:
    ingredient_id (int): the id of the ingredient to which the conversion belongs to; standard value is None
    amount (float): the amount of the ingredient used in the conversion; standard value is None
    unit (str): the unit of the ingredient used in the conversion; standard value is None
    value (float): the value, weight in grams, of the conversion; standard value is None

    Raises:
    ConversionInvalid: Conversion could not be parsed
    ConversionAlreadyExists: Conversion already exists in the database
    """
    try:
        # Check if all parameters are provided
        if (ingredient_id or fdc_id) and (amount is not None) and (unit is not None) and (value is not None):
            if (fdc_id is not None) and (ingredient_id is None):
                # Get the ingredient from the fdc_id
                ingredient = db.session.query(Ingredient).filter_by(fdc_id=fdc_id).first()
            else:
                # Check if the ingredient exists in the database
                ingredient = db.session.query(Ingredient).filter_by(id=ingredient_id).first()

            if ingredient:
                ing_id = ingredient.id
                current_app.logger.debug(f"Updating conversion for ingredient {ing_id} with amount {amount} and unit {unit} and value {value}")

                # Create a new conversion object
                conversion = Conversion(
                    ingredient_id = ing_id,
                    amount = amount,
                    unit = unit,
                    value = value
                )
                db.session.add(conversion)
                new_object = conversion

                # Try to commit the transaction
                try_commit(ing_id)
                current_app.logger.debug(f"Successfully updated conversion for ingredient {ing_id}")
            else:
                new_object = None
        else:
            empty_params = []
            for param, str_rep in zip([fdc_id, ingredient_id, amount, unit, value], ["fdc_id", "ingredient_id", "amount", "unit", "value"]):
                if not param:
                    empty_params.append(str_rep)
            raise Exception(f"Missing parameter(s): {', '.join(empty_params)}")
        
    except Exception as e:
        db.session.rollback()
        raise ElementInvalid(f"Conversion could not be parsed: {str(e)}")
    
    return new_object



def update_nutrition(fdc_id: int = None, ingredient_id: int = None, energy_kj: float = None, energy_kcal: float = None, protein: float = None, fat: float = None, saturated: float = None, carbs: float = None, sugar: float = None, salt: float = None) -> Nutrition:
    """
    This function updates a Nutrition object in the database

    Arguments:
    fdc_id (int): the id as available in the FoodData Central database, standard value is None
    ingredient_id (int): the id of the ingredient to which the nutrition belongs to; standard value is None
    energy_kj (float): the amount of energy in kilojoules; standard value is None
    energy_kcal (float): the amount of energy in kilocalories; standard value is None
    protein (float): the amount of protein in grams; standard value is None
    fat (float): the amount of fat in grams; standard value is None
    saturated (float): the amount of saturated fat in grams; standard value is None
    carbs (float): the amount of carbs in grams; standard value is None
    sugar (float): the amount of sugar in grams; standard value is None
    salt (float): the amount of salt in grams; standard value is None

    Raises:
    ElementInvalid: if the nutrition could not be parsed
    ElementAlreadyExists: if the nutrition already exists in the database
    """
    try:
        # Check if the ingredient_id is provided
        if (ingredient_id is None):
            if (fdc_id is None):
                raise Exception("If ingredient_id is not provided, fdc_id must be provided")
            else:
                # Get the ingredient from the fdc_id
                ingredient = db.session.query(Ingredient).filter_by(fdc_id=fdc_id).first()
        else:
            # Get the ingredient from the ingredient_id
            ingredient = db.session.query(Ingredient).filter_by(id=ingredient_id).first()

        if ingredient:
            ing_id = ingredient.id

            # Check if nutritional info is already in the database
            existing_nutrition = db.session.query(Nutrition).filter_by(ingredient_id=ing_id).first()

            if existing_nutrition:
                current_app.logger.debug(f"Updating nutrition {existing_nutrition.id} for ingredient {ing_id}")

                # Update existing nutrition
                if protein is not None:
                    existing_nutrition.protein = protein
                if fat is not None:
                    existing_nutrition.fat = fat
                if saturated is not None:
                    existing_nutrition.saturated = saturated
                if carbs is not None:
                    existing_nutrition.carbs = carbs
                if sugar is not None:
                    existing_nutrition.sugar = sugar
                if salt is not None:
                    existing_nutrition.salt = salt

                # Check if the energy has to be calculated
                if (energy_kj is not None) and (energy_kcal is not None):
                    existing_nutrition.energy_kj = energy_kj
                    existing_nutrition.energy_kcal = energy_kcal
                else:
                    # Check if the energy can already be calculated
                    p = existing_nutrition.protein
                    f = existing_nutrition.fat
                    c = existing_nutrition.carbs

                    # Check if conversion data exists
                    conversion = db.session.query(NutriConversion).filter_by(ingredient_id=ing_id).first()

                    if (p is not None) and (f is not None) and (c is not None) and (conversion is not None):
                        kcal, kj = calculate_energy(ingredient)
                        existing_nutrition.energy_kj = kj
                        existing_nutrition.energy_kcal = kcal

                new_object = existing_nutrition
            else:
                current_app.logger.debug(f"Creating new nutrition for ingredient {ing_id} with energy values {energy_kj} and {energy_kcal} and nutritional values protein {protein}, fat {fat}, saturated {saturated}, carbs {carbs}, sugar {sugar}, salt {salt}")

                # Create new nutrition object from ingredient_id with energy values
                nutrition = Nutrition(
                    ingredient_id = ing_id,
                    energy_kj = energy_kj,
                    energy_kcal = energy_kcal,
                    protein = protein,
                    fat = fat,
                    saturated = saturated,
                    carbs = carbs,
                    sugar = sugar,
                    salt = salt
                )
                db.session.add(nutrition)
                new_object = nutrition

            # Try to commit the transaction
            try_commit(ing_id)

            current_app.logger.debug(f"Successfully updated nutrition {new_object.id} for ingredient {ing_id}")

        else:
            new_object = None

    except Exception as e:
        db.session.rollback()
        raise ElementInvalid(f"Nutrition could not be parsed: {str(e)}")
    finally:
        return new_object



def update_nutriConversion(fdc_id: int = None, conversion_id: int = None, protein_value: float = None, fat_value: float = None, carb_value: float = None) -> NutriConversion:
    """
    This function updates the nutritional conversion values for a given ingredient.

    Arguments:
    fdc_id (int): the FDC ID of the ingredient; standard value is None
    conversion_id (int): the conversion ID of the ingredient; standard value is None
    protein_value (float): the protein value of the ingredient; standard value is None
    fat_value (float): the fat value of the ingredient; standard value is None
    carb_value (float): the carb value of the ingredient; standard value is None

    Returns:
    NutriConversion: the updated nutritional conversion object

    Raises:
    ElementNotFound: if the ingredient or conversion could not be found in the database
    ElementInvalid: if the conversion could not be parsed
    """
    try:
        # Check if the fdc_id and conversion_id are provided
        if (fdc_id is not None) and (conversion_id is not None):
            # Check if the ingredient exists in the database and fetch the ingredient_id
            existing_ingredient = db.session.query(Ingredient).filter_by(fdc_id=fdc_id).first()

            if existing_ingredient:
                ingredient_id = existing_ingredient.id

                # Check if conversion exists in the database
                existing_conversion = db.session.query(NutriConversion).filter_by(conversion_id=conversion_id).first()

                if existing_conversion:
                    current_app.logger.debug(f"Updating nutritional conversion {existing_conversion.id} for ingredient {ingredient_id}")

                    # Update existing conversion
                    if conversion_id is not None:
                        existing_conversion.conversion_id = conversion_id
                    if protein_value is not None:
                        existing_conversion.protein_value = protein_value
                    if fat_value is not None:
                        existing_conversion.fat_value = fat_value
                    if carb_value is not None:
                        existing_conversion.carb_value = carb_value

                    new_object = existing_conversion
                else:
                    current_app.logger.debug(f"Creating new nutritional conversion for ingredient {ingredient_id} with conversion_id {conversion_id}, protein_value {protein_value}, fat_value {fat_value}, carb_value {carb_value}")

                    # Create new conversion object from ingredient_id
                    conversion = NutriConversion(
                        ingredient_id = ingredient_id,
                        conversion_id = conversion_id,
                        protein_value = protein_value,
                        fat_value = fat_value,
                        carb_value = carb_value
                    )
                    db.session.add(conversion)
                    new_object = conversion
            else:
                new_object = None

        # Check if the just the conversion_id is provided
        elif (conversion_id is not None) and (fdc_id is None):
            # Check if the conversion exists in the database and fetch the ingredient_id
            existing_conversion = db.session.query(NutriConversion).filter_by(conversion_id=conversion_id).first()

            if not existing_conversion:
                new_object = None
            else:
                current_app.logger.debug(f"Updating nutritional conversion {existing_conversion.id} with protein_value {protein_value}, fat_value {fat_value}, carb_value {carb_value}")

                # Update existing conversion
                if protein_value is not None:
                    existing_conversion.protein_value = protein_value
                if fat_value is not None:
                    existing_conversion.fat_value = fat_value
                if carb_value is not None:
                    existing_conversion.carb_value = carb_value

                new_object = existing_conversion

        # If both the fdc_id and conversion_id are not provided, raise an error
        else:
            raise Exception("Conversion ID must be provided")

        # Try to commit the transaction
        try_commit(conversion_id)

        current_app.logger.debug(f"Successfully updated nutritional conversion {new_object.id}")
        
    except Exception as e:
        db.session.rollback()
        raise ElementInvalid(f"NutriConversion could not be parsed: {str(e)}")
    finally:
        return new_object