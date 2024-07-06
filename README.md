# Recipe Nutrient Calculator

The Recipe Nutrient Calculator is a web application that allows users to input a recipe url (from specific webpages) and get detailed nutrient information for each recipe. This application uses the Flask framework and integrates with the USDA FoodData Central API to fetch nutrient data. Additional data can be stored in an SQLite database by uploading a CSV file from the dutch NEVO website or the FoodData Central website.

**! Warning: This application is currently in development and is not fully functional yet and may contain bugs. !**

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

    You can get a `SECRET_KEY` by running `python -c 'import secrets; print(secrets.token_urlsafe())'` in your terminal.
    The standard SQLite database URI can be set to: `sqlite:///site.db`.
    An `USFDC_API_KEY` can be obtained by registering at https://fdc.nal.usda.gov/api-key-signup.html.

5. **Setting up the database:**
    The database is created automatically when the application starts for the first time.
    When using the standard SQLite database URI, the database will be created in the root directory of the project (instance/site.db).

    Add a new *user* (this will be the *admin* account) through the web interface to be able to log in.
    Set the new *user* as *admin* by manually editing the database with a tool such as SQLtools.
    ```SQLite
    UPDATE User SET is_admin = true WHERE id = <your_user_id>;
    ```
    This *user* can then acces the admin-restricted pages through the web interface.

6. **Run the application:**
    ```sh
    flask run
    ```

7. **Access the application:**

    Open your web browser and navigate to `http://127.0.0.1:5000`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please contact Daan Hoepman at [daan.hoepman1508@gmail.com].