import asyncpg
import asyncio
import time
#from CustomExceptions import AlreadyExistsException

#name, file_id

async def start_conn(keys = {"database":"bot", "user":"postgres", "password":"Kirill2016", "host":"localhost"}):
    conn:asyncpg.Connection = await asyncpg.connect(**keys)
    return conn

#colunns_values = {values:[], columns:[]}
async def add(table='audios', **columns_values):
    values = columns_values['values']
    columns = ",".join([value for value in columns_values['columns']])
    vals = ','.join(['${}'.format(i) for i in range(1, len(values) + 1)])
    query = f'''INSERT INTO {table} ({columns})
                VALUES ({vals});'''
    cursor = await start_conn()
    async with cursor.transaction():
        await cursor.execute(query,*values)
    await cursor.close()

async def get_all(table_name='audios'):
    cursor = await start_conn()
    query = f'''SELECT * FROM {table_name};'''
    async with cursor.transaction():
        rows:asyncpg.Record = await cursor.fetch(query)
    await cursor.close()
    return [{key:name for key,name in row.items()} for row in rows]

async def update(old_value, new_value, table_name='audios', column_name='name'):
    cursor = await start_conn()
    query = f'''UPDATE {table_name} SET {column_name} = $1 WHERE {column_name} = $2; '''
    async with cursor.transaction():
        await cursor.execute(query, new_value, old_value)
    await cursor.close()

async def check_if_exist(value:str, table='audios', column_name='name'):
    cursor = await start_conn()
    query = f'''SELECT EXISTS(SELECT * FROM {table} WHERE {column_name} = $1);'''
    async with cursor.transaction():
        row:asyncpg.Record = await cursor.fetchval(query, value)
    await cursor.close()
    return row

async def get_distinct(key_value,table_name='audios', target_name='file_id', key_column='name'):
    cursor = await start_conn()
    query = f'''SELECT {target_name} FROM {table_name} WHERE {key_column} = $1;'''
    async with cursor.transaction():
        row:asyncpg.Record = await cursor.fetchval(query, key_value)
    await  cursor.close()
    return row

async def delete(key_value, table_name='audios', key_column='name'):
    cursor = await start_conn()
    query = f'''DELETE FROM {table_name} WHERE {key_column} = $1'''
    async with cursor.transaction():
        await cursor.execute(query, key_value)
    await cursor.close()

def main():
     pass

if __name__ == '__main__':
    main()
