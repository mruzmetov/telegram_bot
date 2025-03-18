from dotenv import load_dotenv
import os

load_dotenv() # .env faylidan malumotlarni yuklash
env = os.getenv

BOT_TOKEN = env("BOT_TOKEN") # telegram bot tokeni
BOT_NAME = env("BOT_NAME")
DB_HOST = env("DB_HOST")
DB_NAME = env("DB_NAME")
DB_PORT = env("DB_PORT")
DB_PASS = env("DB_PASS")
DB_USER = env("DB_USER")
ADMIN_ID = env("ADMIN_ID")