import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN', '8188476958:AAFP6bxIFOwWhPxbRwlk6pwO1F9JLMV4lvQ')
DB_NAME = 'quiz_bot.db'