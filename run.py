from app import create_app
from app.config import Config

application = create_app(Config)

if __name__ == "__main__":
    application.run(debug=True)