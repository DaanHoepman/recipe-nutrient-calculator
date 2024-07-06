import requests
import json
import os
import string

from .app.utils.recipe_scrapers import scrape_me, scraper_exists_for, AbstractScraper, get_host_name
from flask import render_template
from fuzzywuzzy import fuzz
from langdetect import detect, DetectorFactory
from ingredient_parser import parse_ingredient
from deep_translator import GoogleTranslator

DetectorFactory.seed = 2002

class Recipe_scraper():
    def __init__(self, url: str):
        self.url = url
        self.QUERY_THRESHOLD = 0.5

    def get_translated_recipe(self) -> str:
        return ""

    def get_save_buttons(self) -> str:
        return ""
    
    def get_nutrient_info(self) -> str:
        # Create the scraper if available, otherwise return error
        try:
            scraper = self.__get_scraper()
        except:
            return "ERROR.01: Website ({}) is currently not supported".format(get_host_name(self.url))
        
        # Aquire all necessary metadata of the recipe
        try:
            ingredients = scraper.ingredients()
            yields = scraper.yields().split(' ')[0]
            # print(f"Ingredients: \n{ingredients}")
            # print(f"Yields: {yields}")
            # print(f"\n")
        except:
            return "ERROR.02: Ingredients could not be found"

        # Split the ingredients into (translated, cleaned) ingredient and the amount (converted to grams)
        try:
            en_ing = self.__translate_ingredients(ingredients)
            parsed_ing = self.__parse_ingredients(en_ing)
            # print(f"English Ingredients: \n{en_ing}")
            # print(f"Parsed Ingredients: \n{parsed_ing}")
            # print(f"\n")
        except:
            return "ERROR.03: Ingredients could not be parsed"

        # For all ingredients in the list, run them through the food database and combine with the nutrient information
        #try:
        data = self.__find_nutrition_from_list(parsed_ing)
        print(f"Data: \n{data}")
        print(f"\n")
        #except:
            #return "ERROR.04: Nutrition data could not be derived"

        # Resample the data to return a list of seperate ingredient dictionaries and the totals for the label
        try:
            table_data, label_data = self.__parse_info(self, data, yields)
            print(f"Table Data: \n{table_data}")
            print(f"Label Data: \n{label_data}")
            print(f"\n")
        except:
            return "ERROR.05: Nutrition data could not be parsed"

        # Create the nutrient label and table from the data, html template and css styles
        try:
            nutrition_table = render_template(
                'nutrition_table.html',
                table_data,
            )
        except:
            return "ERROR.06: Nutrition table could not be created"

        try:
            nutrition_label = render_template(
                'nutrition_label.html',
                portion = label_data['Portion (g)'],
                energy_kj = label_data['Energy (kJ)'], 
                energy_kcal = label_data['Energy (kcal)'],
                energy_pp_kj = label_data['Energy (kJ) PP'],
                energy_pp_kcal = label_data['Energy (kcal) PP'],
                fat = label_data['Fat'],
                sat_fat = label_data['Saturated Fat'],
                fat_pp = label_data['Fat PP'],
                sat_fat_pp = label_data['Saturated Fat PP'],
                carb = label_data['Carbohydrates'],
                sugar = label_data['Sugars'],
                carb_pp = label_data['Carbohydrates PP'],
                sugar_pp = label_data['Sugars PP'],
                prot = label_data['Protein'],
                prot_pp = label_data['Protein PP'],
                salt = label_data['Salt'],
                salt_pp = label_data['Salt PP'],
            )
        except:
            return "ERROR.07: Nutrition label could not be created"

        return nutrition_table + nutrition_label

    def __get_scraper(self) -> AbstractScraper:
        if scraper_exists_for(self.url):
            return scrape_me(self.url)
        else:
            return scrape_me(self.url, wild_mode=True)
        
    def __parse_info(self, data: dict[float, dict[float]], yields: int) -> tuple[list[dict], dict[float]]:
        table_data = []
        info_container = {
            'Portion (g)': 0,
            'Energy (kJ)': 0,
            'Energy (kJ) PP': 0,
            'Energy (kcal)': 0,
            'Energy (kcal) PP': 0,
            'Fat': 0,
            'Fat PP': 0,
            'Saturated Fat': 0,
            'Saturated Fat PP': 0,
            'Carbohydrates': 0,
            'Carbohydrates PP': 0,
            'Sugars': 0,
            'Sugars PP': 0,
            'Protein': 0,
            'Protein PP': 0,
            'Salt': 0,
            'Salt PP': 0
        }
        
        for name, values in data.items():
            # Aquire metadata
            amount = values['Amount']
            nut = values['Info']
            portion_size = amount / yields

            # Aquire nutritional data
            energy_kj = nut['energy_kj']
            energy_kcal = nut['energy_kcal']
            fat = nut['fat']
            sat_fat = nut['sat_fat']
            carb = nut['carb']
            sugar = nut['sugar']
            protein = nut['prot']
            salt = nut['salt']

            # Create the dictionary to store all values in
            ingredient = {
                'name': name,
                'amount': self.__cast_to_round(amount),
                'energy_kJ': self.__cast_to_round(energy_kj * amount),
                'energy_kcal': self.__cast_to_round(energy_kcal * amount),
                'fat': self.__cast_to_round(fat * amount),
                'sat_fat': self.__cast_to_round(sat_fat * amount),
                'carb': self.__cast_to_round(carb * amount),
                'sugar': self.__cast_to_round(sugar * amount),
                'protein': self.__cast_to_round(protein * amount),
                'salt': self.__cast_to_round(salt * amount)
            }

            # Append the ingredient to the table data, finishing the tabular part
            table_data.append(ingredient)

            # For the label: sum the individual nutritional facts to the container values
            info_container['Portion (g)'] += portion_size
            info_container['Energy (kJ)'] += energy_kj * 100
            info_container['Energy (kJ) PP'] += energy_kj * portion_size
            info_container['Energy (kcal)'] += energy_kcal * 100
            info_container['Energy (kcal) PP'] += energy_kcal * portion_size
            info_container['Fat'] += fat * 100
            info_container['Fat PP'] += fat * portion_size
            info_container['Saturated Fat'] += sat_fat * 100
            info_container['Saturated Fat PP'] += sat_fat * portion_size
            info_container['Carbohydrates'] += carb * 100
            info_container['Carbohydrates PP'] += carb * portion_size
            info_container['Sugars'] += sugar * 100
            info_container['Sugars PP'] += sugar * portion_size
            info_container['Protein'] += protein * 100
            info_container['Protein PP'] += protein * portion_size
            info_container['Salt'] += salt * 100
            info_container['Salt PP'] += salt * portion_size

        # For every instance in the info container, cast them to the proper rounded value
        for key, value in info_container.items():
            info_container[key] = self.__cast_to_round(value)

        return (table_data, info_container)
        
    def __cast_to_round(self, num: float) -> str:
        match num:
            case num if num.is_integer():
                return str(num)
            case num if num >= 10:
                return str(round(num))
            case num if num >= 1:
                return str(round(num, 1))
            case num if num >= 0.1:
                return str(round(num, 1))
            case num if num >= 0.005:
                return str(round(num, 2))
            case num if num > 0:
                return '~0'
            case _:
                return '0'

    def __translate_ingredients(self, ingredients: list[str], language_to: str = 'en') -> list[str]:
        result = []

        for ing in ingredients:
            # Check if current language is already equal to the target language
            if detect(ing) == language_to:
                result.append(ing)
            else:
                # Translate the text to the target language
                translated_text = GoogleTranslator(source='auto', target=language_to).translate(ing)
                result.append(translated_text)

        return result
    
    def __parse_ingredients(self, ingredients: list[str]) -> list[dict[str, float, str]]:
        parsed_list = []

        for ing in ingredients:
            # Split the ingredient line into name and amount
            try:
                parsed = parse_ingredient(ing, string_units=True)
                name = parsed.name.text
                amount = parsed.amount
                quantity = None
                unit = None
            except:
                raise Exception("Ingredient: '{}', cannot be parsed".format(ing))

            if len(amount) > 1:
                # If the amount contains multiple measurements, choose the best fit
                for am in amount:
                    # Choose the unit which has no approximation
                    if not am.APPROXIMATE:
                        quantity = am.quantity
                        unit = am.unit
                
                # Check if at least one is stored, else store the first amount
                if (quantity is None) or (unit is None):
                    quantity = amount[0].quantity
                    unit = amount[0].unit
            elif len(amount) == 0:
                # If the amount contains no data, set the quantity to 0 and unit to blank
                quantity = 0
                unit = ""
            else:
                # If the amount contains only one measurement, choose the first
                quantity = amount[0].quantity
                unit = amount[0].unit

            parsed_list.append({'Name': name, 'Quantity': quantity, 'Unit': unit})

        # Remove all ingredients from the list which have no amount
        return [x for x in parsed_list if x['Quantity'] != 0]
    
    def __find_nutrition_from_list(self, parsed_ingredients: list[dict[str, float, str]]) -> dict[float, dict[float]]:
        information_collection = {}

        # For every ingredient in the list, find the nutrients included in the recipe
        for ingredient in parsed_ingredients:
            # Find the best fitting item from the FoodCentral Database
            fdcId = self.fdcId_retrieval(ingredient["Name"])
            print(f"FooData Central Id: {fdcId} \t\t\t Name: {ingredient['Name']}")

            # If no item can be found, do not include this ingredient in the calculation
            if fdcId is None:
                continue

            # Find the nutrients (per 100 gram) and the weight this ingredient adds to the recipe
            name, nutrition, weight = self.nutrient_retrieval(fdcId, ingredient)

            # Store the information along with the database ingredient name and amount used in the recipe
            information_collection[name] = {'Amount': weight, 'Info': nutrition}

        return information_collection

    
    def __nutrition_per_gram(self, nutrients: dict) -> dict[float]:
        # Generate the information on nutrition per gram from the raw data
        nut = {
            'energy_kj': nutrients['number' == 268]['amount'] / 100.0,
            'energy_kcal': nutrients['number' == 208]['amount'] / 100.0,
            'fat': nutrients['number' == 204]['amount'] / 100.0,
            'sat_fat': nutrients['number' == 606]['amount'] / 100.0,
            'carb': nutrients['number' == 205]['amount'] / 100.0,
            'sugar': nutrients['number' == 269]['amount'] / 100.0,
            'prot': nutrients['number' == 203]['amount'] / 100.0,
            'salt': nutrients['number' == 307]['amount'] / 100.0
        }

        return nut

    def __to_gram_conversion(self, portions: dict, quantity: float, unit: str) -> float:      
        # Check if the unit has a value
        if unit == '':
            # Return the average of all units in the portions data
            return sum([el['gramWeight'] for el in portions]) / len(portions)
        
        possible_values = ['g', 'gr', 'gm', 'grm', 'gram', 'grams', 'gms', 'grms', 'grmms', 'gramms', 'gramm']
        
        # Check if the unit already is in grams, and if so return standard value
        if unit.translate(str.maketrans('','',string.punctuation)).lower() in possible_values:
            return quantity
        
        # Find the best conversion from the portions data
        possible_conversions = [el['modifier'] for el in portions]
        best_conversion = None
        best_ratio = 0

        for poss in possible_conversions:
            try:
                curr_ratio = fuzz.token_set_ratio(poss, unit)
                if curr_ratio > best_ratio:
                    best_conversion = poss
                    best_ratio = curr_ratio
            except:
                pass

        # Return the amount by the best conversion to grams
        if best_conversion is None:
            return 0
        
        return portions['modifier' == best_conversion]['gramWeight']