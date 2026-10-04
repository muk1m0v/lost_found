from mukimov.color import green, red
from dotenv import load_dotenv
from os import getenv
import asyncpg

load_dotenv()

async def get_connection():
    try:
        conn = await asyncpg.connect(
            database=getenv('DB_NAME'),
            user=getenv('DB_USER'),
            password=getenv('DB_PASS'),
            host=getenv('DB_HOST'),
            port=getenv('DB_PORT')
        )
        print(green('Database Connected!'))
        return conn
    except Exception as err:
        print(red(f'Connected Database Error: {err}'))

async def init_tables():
    conn = await get_connection()
    try:
        with open("services/lost_found.sql", "r") as file:
            sql = file.read()
        await conn.execute(sql)
        print(green("Tables created!"))
    except Exception as err:
        print(red(f"Create tables error: {err}"))
    finally:
        await conn.close()
