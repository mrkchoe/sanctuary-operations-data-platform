try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass  # no .env loading; use env vars or app defaults

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
