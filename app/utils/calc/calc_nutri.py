from app import db
from app.models import Ingredient, Nutrition, Conversion

#--------------------

def process_ingredients(ingredient_list: list[str]) -> dict:
    """
    
    """
    nutri_dict = {
        'energy_kj': 0,
        'energy_kcal': 0,
        'protein': 0,
        'fat': 0,
        'saturated': 0,
        'carbs': 0,
        'sugar': 0,
        'salt': 0
    }
    na_ingredients = []
    used_ingredients = []

    for ingredient_line in ingredient_list:
        # Parse string into ingredient
        ingredient, amount, unit = parse_ingredient(ingredient_line)

        # Find the best matching ingredient in the database
        best_ingredient, likeliness = find_best_match_db(ingredient)

        if likeliness > THRESHOLD:
            # Search for the corresponding nutritional values in the database
            nutri = db.session.query(Nutrition).filter_by(ingredient_id=best_ingredient.id).first()

            if nutri:
                # Converse the ingredient amount into grams
                grams = convert_amount_db(best_ingredient, amount, unit)

                # Update nutrition dictionary with values from the database
                nutri_dict['energy_kj'] += nutri.energy_kj * grams
                nutri_dict['energy_kcal'] += nutri.energy_kcal * grams
                nutri_dict['protein'] += nutri.protein * grams
                nutri_dict['fat'] += nutri.fat * grams
                nutri_dict['saturated'] += nutri.saturated * grams
                nutri_dict['carbs'] += nutri.carbs * grams
                nutri_dict['sugar'] += nutri.sugar * grams
                nutri_dict['salt'] += nutri.salt * grams

                # Mark ingredient as used
                info = {
                    'og_name': ingredient,
                    'used_name': best_ingredient.name,
                    'og_amount': amount,
                    'used_amount': grams,
                    'og_unit': unit,
                    'used_unit': 'g',
                    'likeliness': likeliness
                }
                used_ingredients.append(info)
            else:
                # Mark ingredient as not found
                na_ingredients.append((ingredient, "No Nutritional values found in database"))
        else:
            # If the likeliness is below the threshold, query the FDC API for a possibly better ingredient
            fdc_id, new_like = find_best_match_API(ingredient)

            # Check if new founds are better than the old ones
            if (new_like > likeliness) and (new_like > THRESHOLD):
                info, nutri, conversion = extract_API_info(fdc_id)

                if nutri:
                    # Converse the ingredient amount into grams
                    grams = convert_amount_API(conversion, amount, unit)

                    # Update nutrition dictionary with values from the API response
                    nutri_dict['energy_kj'] += nutri['energy_kj'] * grams
                    nutri_dict['energy_kcal'] += nutri['energy_kcal'] * grams
                    nutri_dict['protein'] += nutri['protein'] * grams
                    nutri_dict['fat'] += nutri['fat'] * grams
                    nutri_dict['saturated'] += nutri['saturated'] * grams
                    nutri_dict['carbs'] += nutri['carbs'] * grams
                    nutri_dict['sugar'] += nutri['sugar'] * grams
                    nutri_dict['salt'] += nutri['salt'] * grams

                    # Mark ingredient as used
                    info = {
                        'og_name': ingredient,
                        'used_name': info['name'],
                        'og_amount': amount,
                        'used_amount': grams,
                        'og_unit': unit,
                        'used_unit': 'g',
                        'likeliness': new_like
                    }
                    used_ingredients.append(info)
                else:
                    # Mark ingredient as not found
                    na_ingredients.append((ingredient, "No Nutritional values found in API"))
            else:
                # Mark ingredient as not found
                na_ingredients.append((ingredient, "No sufficient match found in database or API"))

    # Return dictionary with nutrition values and list of used / not available ingredients
    return {
        'nutri': nutri_dict,
        'used_ingredients': used_ingredients,
        'error_ingredients': na_ingredients
    }