import aiosqlite
from config import DB_NAME

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                          (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_answers 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, question_index INTEGER, attempt INTEGER, is_correct INTEGER)''')
        await db.commit()

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)',
                        (user_id, index))
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def save_quiz(user_id, quiz_list):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT MAX(attempt) FROM quiz_answers WHERE user_id = ?',
                              (user_id,)) as cursor:
            result = await cursor.fetchone()
        attempt = (result[0] or 0) + 1

        i = 1
        for answer in quiz_list:
            await db.execute('INSERT OR REPLACE into quiz_answers (user_id, question_index, attempt, is_correct) VALUES (?, ?, ?, ?)', (user_id, i, attempt, 1 if answer['is_correct'] else 0))
            await db.commit()
            i += 1
