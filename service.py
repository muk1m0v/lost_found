from services.db import get_connection
from mukimov.color import red

async def get_users():
    conn = await get_connection()
    try:
        rows = await conn.fetch('SELECT * FROM users ORDER BY id')
        return rows
    except Exception as err:
        print(red(f'Get Users Error: {err}'))
        return []
    finally:
        await conn.close()

async def check_users(telegram_id):
    conn = await get_connection()
    try:
        rows = await conn.fetch('SELECT * FROM users WHERE telegram_id = $1', str(telegram_id))
        return rows
    except Exception as err:
        print(red(f'Check Users Error: {err}'))
        return []
    finally:
        await conn.close()

async def save_user(telegram_id, username, full_name):
    conn = await get_connection()
    try:
        await conn.execute('INSERT INTO users (telegram_id, username, full_name) VALUES ($1, $2, $3)', str(telegram_id), username, full_name)
    except Exception as err:
        print(red(f'Add Users Error: {err}'))
    finally:
        await conn.close()

async def save_item(owner_id, title, description, location, photo_file_id):
    conn = await get_connection()
    try:
        row = await conn.fetchrow("INSERT INTO items (owner_id, title, description, location, photo_file_id, status) VALUES ($1, $2, $3, $4, $5, 'available') RETURNING id", int(owner_id), title, description, location, photo_file_id)
        return row
    except Exception as err:
        print(red(f'Save Item Error: {err}'))
        return None
    finally:
        await conn.close()

async def get_items():
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT * FROM items WHERE status = 'available' ORDER BY id")
        return rows
    except Exception as err:
        print(red(f'Get Items Error: {err}'))
        return []
    finally:
        await conn.close()

async def get_item(item_id):
    conn = await get_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM items WHERE id = $1', int(item_id))
        return row
    except Exception as err:
        print(red(f'Get Item Error: {err}'))
        return None
    finally:
        await conn.close()

async def get_claim(user_id, item_id):
    conn = await get_connection()
    try:
        row = await conn.fetchrow('SELECT * FROM claims WHERE user_id = $1 AND item_id = $2', int(user_id), int(item_id))
        return row
    except Exception as err:
        print(red(f'Get Claim Error: {err}'))
        return None
    finally:
        await conn.close()

async def new_claim(user_id, item_id):
    conn = await get_connection()
    try:
        item = await conn.fetchrow('SELECT * FROM items WHERE id = $1', int(item_id))
        if item is None:
            return 'no_item'
        if item['status'] != 'available':
            return 'returned'
        if int(item['owner_id']) == int(user_id):
            return 'own'
        old = await conn.fetchrow('SELECT id FROM claims WHERE user_id = $1 AND item_id = $2', int(user_id), int(item_id))
        if old is not None:
            return 'already'
        await conn.execute("INSERT INTO claims (user_id, item_id, status) VALUES ($1, $2, 'pending')", int(user_id), int(item_id))
        return 'ok'
    except Exception as err:
        print(red(f'Add Claim Error: {err}'))
        return None
    finally:
        await conn.close()

async def my_claims(telegram_id):
    conn = await get_connection()
    try:
        rows = await conn.fetch('SELECT claims.id, claims.status, claims.item_id, items.title FROM claims JOIN items ON items.id = claims.item_id WHERE claims.user_id = $1 ORDER BY claims.id', int(telegram_id))
        return rows
    except Exception as err:
        print(red(f'My Claims Error: {err}'))
        return []
    finally:
        await conn.close()

async def pending_claims(item_id):
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT * FROM claims WHERE item_id = $1 AND status = 'pending' ORDER BY id", int(item_id))
        return rows
    except Exception as err:
        print(red(f'Pending Claims Error: {err}'))
        return []
    finally:
        await conn.close()

async def approve_claim(claim_id, owner_id):
    conn = await get_connection()
    try:
        async with conn.transaction():
            claim = await conn.fetchrow('SELECT * FROM claims WHERE id = $1', int(claim_id))
            if claim is None:
                return 'no_claim'
            item = await conn.fetchrow('SELECT * FROM items WHERE id = $1', int(claim['item_id']))
            if item is None:
                return 'no_item'
            if int(item['owner_id']) != int(owner_id):
                return 'not_owner'
            if item['status'] != 'available':
                return 'returned'
            if claim['status'] != 'pending':
                return 'done'
            await conn.execute("UPDATE claims SET status = 'approved' WHERE id = $1", int(claim_id))
            await conn.execute("UPDATE items SET status = 'returned' WHERE id = $1", int(claim['item_id']))
            await conn.execute("UPDATE claims SET status = 'rejected' WHERE item_id = $1 AND status = 'pending' AND id != $2", int(claim['item_id']), int(claim_id))
            return 'ok'
    except Exception as err:
        print(red(f'Approve Claim Error: {err}'))
        return None
    finally:
        await conn.close()
