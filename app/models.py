import json

from flask_login import UserMixin

from app import db, lm
from app.utils.authentication import hash_pass

#--------------------

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(128))
    password = db.Column(db.LargeBinary)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]

            if property == 'password':
                value = hash_pass(value)

            setattr(self, property, value)

    def __repr__(self):
        return f"<User {self.username}>"
    
    @lm.user_loader
    def user_loader(id):
        return User.query.filter_by(id=id).first()
    
    @lm.request_loader
    def request_loader(request):
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        return user if user else None
    

class Ingredient(db.Model):

    __tablename__ = 'Ingredient'

    id = db.Column(db.Integer, primary_key=True)
    name_nl = db.Column(db.String(100), unique=False, nullable=True)
    name_en = db.Column(db.String(100), unique=False, nullable=True)
    nevo_id = db.Column(db.Integer, unique=True, nullable=True)
    fdc_id = db.Column(db.Integer, unique=True, nullable=True)
    synonyms = db.Column(db.Text, unique=False, nullable=True)
    unit = db.Column(db.String(10), unique=False, nullable=True)
    nutrition = db.relationship('Nutrition', backref='Ingredient', lazy=True)
    conversion = db.relationship('Conversion', backref='Ingredient', lazy=True)
    nutri_conversion = db.relationship('NutriConversion', backref='Ingredient', lazy=True)

    def __repr__(self):
        return f"<Ingredient {self.name_en}>"
    
    @property
    def synonym_list(self) -> list[str]:
        """
        This function converts the synonyms JSON string to a python list

        Arguments:
            self: The object itself

        Returns:
            list: A list of synonyms

        Raises:
            Exception:  If the synonyms JSON string is not valid JSON
        """
        return json.loads(self.synonyms) if self.synonyms else []
    
    @synonym_list.setter
    def synonym_list(self, value: list[str]) -> None:
        """
        This function converts the synonyms list to a JSON string for storage

        Arguments:
            self: The object itself
            value (list[str]):  The list of synonyms

        Returns:
            None

        Raises:
            Exception:  If the synonyms JSON string is not valid JSON
        """
        self.synonyms = json.dumps(value)


class Conversion(db.Model):

    __tablename__ = 'Conversion'

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('Ingredient.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, unique=False, nullable=False)
    unit = db.Column(db.String(84), unique=False, nullable=True)
    value = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        return f"<Conversion {self.id}>"

    
class Nutrition(db.Model):

    __tablename__ = 'Nutrition'
    
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('Ingredient.id'), nullable=False)
    energy_kj = db.Column(db.Float, unique=False, nullable=True)
    energy_kcal = db.Column(db.Float, unique=False, nullable=True)
    protein = db.Column(db.Float, unique=False, nullable=True)
    fat = db.Column(db.Float, unique=False, nullable=True)
    saturated = db.Column(db.Float, unique=False, nullable=True)
    carbs = db.Column(db.Float, unique=False, nullable=True)
    sugar = db.Column(db.Float, unique=False, nullable=True)
    salt = db.Column(db.Float, unique=False, nullable=True)

    def __repr__(self):
        return f"<Nutrition {self.id}>"
    
class NutriConversion(db.Model):

    __tablename__ = 'NutriConversion'

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('Ingredient.id'), nullable=False)
    conversion_id = db.Column(db.Integer, unique=True, nullable=False)
    protein_value = db.Column(db.Float, unique=False, nullable=True)
    fat_value = db.Column(db.Float, unique=False, nullable=True)
    carb_value = db.Column(db.Float, unique=False, nullable=True)

    def __repr__(self):
        return f"<NutriConversion {self.id}>"
