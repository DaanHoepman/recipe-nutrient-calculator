# Recipe Nutrient Calculator

The Recipe Nutrient Calculator is a web application that allows users to input a recipe url (from specific webpages) and get detailed nutrient information for each recipe. This application uses the Python Flask framework and integrates with the USDA FoodData Central API to fetch nutrient data. Additional data can be stored in an SQLite database by uploading a CSV file from the dutch NEVO website or the FoodData Central website.

**! Warning: This application is currently in development and is not fully functional yet !**

## Features

- Input recipe url
- Fetch detailed nutrient information for each recipe (*in progress*)
- User authentication and management
- Store and manage ingredient data in an SQLite database

## Getting Started

### Prerequisites

- Python 3.x
- SQLite database

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/DaanHoepman/recipe-nutrient-calculator.git
    cd recipe-nutrient-calculator
    ```

2. **Set up a virtual environment:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.\venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add the following variables:
    ```.env
    SECRET_KEY=<your_secret_key>
    DATABASE_URL=<your_sqlite_database_uri>
    USFDC_API_KEY=<your_usda_api_key>
    ```

    You can get a `SECRET_KEY` by running the following command in your terminal:
    ```sh
    python -c 'import secrets; print(secrets.token_urlsafe())'
    ```
    The standard SQLite database URI can be set to: `sqlite:///site.db`.
    An `USFDC_API_KEY` can be obtained by registering at https://fdc.nal.usda.gov/api-key-signup.html.

5. **Run the application:**
    ```sh
    flask run
    ```

6. **Access the application:**

    Open your web browser and navigate to `http://127.0.0.1:5000`.

#### Database Initialization

7. **Setting up the database:**

    The empty database is created automatically when the application starts for the first time.
    When using the standard SQLite database URI, the database will be created in the root directory of the project (`instance/site.db`).

    Make sure to add a new *user* (this will be the *admin* account) through the web interface to be able to log in.
    Set the new *user* as *admin* by manually editing the database with a tool such as SQLtools.
    ```SQLite
    UPDATE User SET is_admin = true WHERE id = <your_user_id>;
    ```
    This *user* can then access the admin-restricted pages through the web interface.

8. **Importing ingredient data:**

    The admin pages `/load_nevo` and `/load_fdc` can be used to import data from the dutch NEVO website and the FoodData Central website respectively.
    Simply drag and drop the CSV file(s) on the pages and submit to update the database.

    If an ingredient already exists in the database, the data will be updated. Otherwise, a new ingredient will be added.

    Accepted files for the NEVO ingredients from https://www.rivm.nl/en/dutch-food-composition-database/nevo-online-request-dataset:
    - `NEVO[year]_[version].csv`

    Acceptec files for the FDC ingredients from https://fdc.nal.usda.gov/download-datasets.html:
    - `food_calorie_conversion_factor.csv`
    - `food_nutrient_conversion_factor.csv`
    - `food_nutrient.csv`
    - `food_portion.csv`
    - `food.csv`

    If any of these files are missing, only the information provided will be updated in the database.

    Only the ingredients present in `food.csv` will be updated. To specify which ingredient groups to update,
    edit the `TO_SCRAPE` variable in the `app/utils/data/__init__.py` file to include Foundation Foods, SR Legacy, FNDDS or Branded.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please contact Daan Hoepman at [daan.hoepman1508@gmail.com].