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


async def get_quiz_statistics():
    async with aiosqlite.connect(DB_NAME) as db:
        statistics = {}

        # 1. Общее количество игроков
        async with db.execute('SELECT COUNT(DISTINCT user_id) FROM quiz_answers') as cursor:
            statistics['total_players'] = (await cursor.fetchone())[0]

        # 2. Общее количество ответов
        async with db.execute('SELECT COUNT(*) FROM quiz_answers') as cursor:
            statistics['total_answers'] = (await cursor.fetchone())[0]

        # 3. Количество правильных ответов
        async with db.execute('SELECT COUNT(*) FROM quiz_answers WHERE is_correct = 1') as cursor:
            statistics['correct_answers'] = (await cursor.fetchone())[0]

        # 4. Процент правильных ответов
        if statistics['total_answers'] > 0:
            statistics['correct_percentage'] = round(
                (statistics['correct_answers'] / statistics['total_answers']) * 100, 2)
        else:
            statistics['correct_percentage'] = 0

        # 5. Самый сложный вопрос (с наименьшим процентом правильных ответов)
        async with db.execute('''
                              SELECT question_index,
                                     COUNT(*)                                     as total_attempts,
                                     SUM(is_correct)                              as correct_attempts,
                                     ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as success_rate
                              FROM quiz_answers
                              GROUP BY question_index
                              ORDER BY success_rate ASC LIMIT 1
                              ''') as cursor:
            hardest_question = await cursor.fetchone()
            if hardest_question:
                statistics['hardest_question'] = {
                    'index': hardest_question[0],
                    'success_rate': hardest_question[3]
                }

        # 6. Самый легкий вопрос (с наибольшим процентом правильных ответов)
        async with db.execute('''
                              SELECT question_index,
                                     ROUND(SUM(is_correct) * 100.0 / COUNT(*), 2) as success_rate
                              FROM quiz_answers
                              GROUP BY question_index
                              ORDER BY success_rate DESC LIMIT 1
                              ''') as cursor:
            easiest_question = await cursor.fetchone()
            if easiest_question:
                statistics['easiest_question'] = {
                    'index': easiest_question[0],
                    'success_rate': easiest_question[1]
                }

        # 8. Топ игроков по количеству правильных ответов
        async with db.execute('''
                              SELECT user_id, COUNT(*) as correct_answers
                              FROM quiz_answers
                              WHERE is_correct = 1
                              GROUP BY user_id
                              ORDER BY correct_answers DESC LIMIT 5
                              ''') as cursor:
            statistics['top_players'] = await cursor.fetchall()

        return statistics