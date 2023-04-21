import datetime
import os
from hashlib import sha256

from fastapi_asyncpg import configure_asyncpg
from lib.app_init import app
from fastapi import Depends

password = os.environ.get("DATABASE_PASS")
host = os.environ.get("DATABASE_HOST")
port = os.environ.get("DATABASE_PORT")
db_name = os.environ.get("DATABASE_NAME")

password = 102015 if password is None else password
host = '127.0.0.1' if host is None else host
port = 5432 if port is None else port
db_name = 'cleaner_api' if db_name is None else db_name

# Создаем новую таблицу
data_b = configure_asyncpg(app, f'postgres://postgres:{password}@{host}:{port}/{db_name}')


async def create_all_users_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS all_users (
 user_id SERIAL PRIMARY KEY,
 phone BIGINT UNIQUE DEFAULT 0,
 email TEXT DEFAULT '0',
 name TEXT DEFAULT '0',
 image_link TEXT DEFAULT '0',
 auth_type TEXT DEFAULT '0',
 auth_id BIGINT DEFAULT 0,
 description TEXT DEFAULT '0',
 lang TEXT DEFAULT 'en',
 city TEXT DEFAULT '0',
 street TEXT DEFAULT '0',
 house TEXT DEFAULT '0',
 score BIGINT DEFAULT 5,
 score_count BIGINT DEFAULT 0,
 total_score BIGINT DEFAULT 0,
 status TEXT DEFAULT 'worker',
 range BIGINT DEFAULT 500,
 longitudes DOUBLE PRECISION,
 latitudes DOUBLE PRECISION,
 push TEXT DEFAULT '0',
 last_active timestamp,
 create_date timestamp)''')


# Создаем новую таблицу
async def create_token_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS token (
 id SERIAL PRIMARY KEY,
 user_id BIGINT DEFAULT 0,
 token TEXT DEFAULT '0',
 token_type TEXT DEFAULT 'access',
 change_password INTEGER DEFAULT 0,
 create_date timestamp,
 death_date timestamp
 )''')


# Создаем новую таблицу
async def create_work_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS work (
 id SERIAL PRIMARY KEY,
 user_id BIGINT DEFAULT 0,
 work_type TEXT DEFAULT 'clean',
 object_id INTEGER DEFAULT 0,
 object_size INTEGER DEFAULT 0
 )''')


# Создаем новую таблицу
async def create_work_type_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS object_type (
 id SERIAL PRIMARY KEY,
 name_ru TEXT DEFAULT 'room',
 name_en TEXT DEFAULT 'room',
 name_heb TEXT DEFAULT 'room'
 )''')
    object_types = ((1, 'Квартира', 'Apartment', 'דִירָה'), (2, 'Дом', 'House', 'בַּיִת'),
                    (3, 'Офис', 'Office', 'מִשׂרָד'), (4, 'Легковой автомобиль', 'Car', 'מכונית'))
    for i in object_types:
        await db.execute(f"INSERT INTO object_type (id, name_ru, name_en, name_heb) "
                         f"VALUES ($1, $2, $3, $4) "
                         f"ON CONFLICT DO NOTHING;", i[0], i[1], i[2], i[3])


# Создаем новую таблицу
# Таблица для записи статей затрат в одном счете
async def create_files_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS files (
 id SERIAL PRIMARY KEY,
 file_name TEXT DEFAULT '0',
 file_path TEXT DEFAULT '0',
 file_type TEXT DEFAULT '0',
 owner_id INTEGER DEFAULT 0,
 create_date timestamp
 )''')


# Создаем новую таблицу
async def create_user(db: Depends, phone, email, name, auth_type, auth_id, description, lang, city, street, house,
                      status, longitudes, latitudes, image_link: str):
    now = datetime.datetime.now()
    user_id = await db.fetch(f"INSERT INTO all_users (phone, email, name, auth_type, auth_id, description, lang, "
                             f"city, street, house, status, longitudes, latitudes, image_link, last_active, create_date) "
                             f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16) "
                             f"ON CONFLICT DO NOTHING RETURNING user_id;", phone, email, name, auth_type, auth_id,
                             description, lang, city, street, house, status, longitudes, latitudes, image_link, now,
                             now)
    return user_id


# Создаем новую таблицу
async def save_users_work(db: Depends, user_id: int, work_type: str, object_id: int, object_size: int):
    await db.fetch(f"INSERT INTO work (user_id, work_type, object_id, object_size) "
                   f"VALUES ($1, $2, $3, $4) "
                   f"ON CONFLICT DO NOTHING;", user_id, work_type, object_id, object_size)
    return user_id


# Создаем новую таблицу
async def create_token(db: Depends, user_id, token_type):
    create_date = datetime.datetime.now()
    if token_type == 'access':
        death_date = create_date + datetime.timedelta(minutes=30)
    else:
        death_date = create_date + datetime.timedelta(days=30)
    now = datetime.datetime.now()
    token = sha256(f"{user_id}.{now}".encode('utf-8')).hexdigest()
    token = await db.fetch(f"INSERT INTO token (user_id, token, token_type, create_date, death_date) "
                           f"VALUES ($1, $2, $3, $4, $5) "
                           f"ON CONFLICT DO NOTHING RETURNING token;", user_id, token, token_type,
                           create_date, death_date)
    return token


# Создаем новую запись в базе данных
async def save_new_file(db: Depends, file_name: str, file_path: str, file_type: str, owner_id: int):
    now = datetime.datetime.now()
    file_id = await db.fetch(f"INSERT INTO files (file_name, file_path, file_type, owner_id, create_date) "
                             f"VALUES ($1, $2, $3, $4, $5) "
                             f"ON CONFLICT DO NOTHING RETURNING id;", file_name, file_path, file_type, owner_id, now)
    return file_id


# Создаем новую таблицу
async def read_data(db: Depends, table: str, id_name: str, id_data, name: str):
    data = await db.fetch(f"SELECT {name} FROM {table} WHERE {id_name} = $1;", id_data)
    return data


# Создаем новую таблицу
async def read_all(db: Depends, table: str, name: str = '*'):
    data = await db.fetch(f"SELECT {name} FROM {table};")
    return data


# Создаем новую таблицу
async def read_data_2_were(db: Depends, table: str, id_name1: str, id_name2: str, id_data1, id_data2, name: str):
    data = await db.fetch(f"SELECT {name} FROM {table} WHERE {id_name1} = $1 AND  {id_name2} = $1;", id_data1, id_data2)
    return data


# Создаем новую таблицу
async def get_token(db: Depends, token_type: str, token: str):
    now = datetime.datetime.now()
    data = await db.fetch(f"SELECT user_id FROM token "
                          f"WHERE token_type = $1 "
                          f"AND token = $2 "
                          f"AND death_date > $3 "
                          f"AND change_password = 0;",
                          token_type, token, now)
    return data


# Создаем новую таблицу
async def get_token_admin(db: Depends, token_type: str, token: str):
    now = datetime.datetime.now()
    data = await db.fetch(f"SELECT user_id FROM token "
                          f"WHERE token_type = $1 "
                          f"AND status = admin "
                          f"AND token = $2 "
                          f"AND death_date > $3 "
                          f"AND change_password = 0;",
                          token_type, token, now)
    return data


# Создаем новую таблицу
async def update_user(db: Depends, name: str, phone: int, email: str, description: str, lang: str, city: str,
                      house: str,
                      street: str, latitudes: float, longitudes: float, status: str, range: int, user_id: int):
    user_id = await db.fetch(f"UPDATE all_users SET name=$1, phone=$2, email=$3, description=$4, lang=$5, city=$6, "
                             f"street=$7, house=$8, latitudes=$9, longitudes=$10, status=$11, range=$12 WHERE "
                             f"user_id=$13;",
                             name, phone, email, description, lang, city, street, house, latitudes, longitudes,
                             status, range, user_id)
    return user_id


# Обновляем информацию
async def update_data(db: Depends, table: str, name: str, id_data, data, id_name: str = 'id'):
    await db.execute(f"UPDATE {table} SET {name}=$1 WHERE {id_name}=$2;",
                     data, id_data)


# Обновляем информацию
async def update_user_active(db: Depends, user_id: int):
    now = datetime.datetime.now()
    await db.fetch(f"UPDATE all_users SET last_active=$1 WHERE user_id=$2;",
                   now, user_id)


# Обновляем информацию
async def update_password(db: Depends, user_id: int, password_hash: str):
    await db.fetch(f"UPDATE all_users SET password_hash=$1 WHERE user_id=$2;",
                   password_hash, user_id)


# Удаляем токены
async def delete_old_tokens(db: Depends):
    now = datetime.datetime.now()
    await db.execute(f"DELETE FROM token WHERE death_date < $1", now)


# Удаляем токены
async def delete_all_tokens(db: Depends, user_id: int):
    await db.execute(f"DELETE FROM token WHERE user_id = $1", user_id)


# Удаляем все записи из таблицы по ключу
async def delete_where(db: Depends, table: str, id_name: str, data):
    await db.execute(f"DELETE FROM {table} WHERE {id_name} = $1", data)
