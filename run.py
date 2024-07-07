from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) # ! Make sure to change this to False when deploying