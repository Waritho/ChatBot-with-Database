import sqlite3
import hashlib
import os
import uuid
from datetime import datetime

# Use absolute path to ensure we always use the same database file
# regardless of where the script is run from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'chatbot.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Ensure we can see all committed changes immediately (important for WAL mode)
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_threads table to link threads to users
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_threads (
            user_id INTEGER,
            thread_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, thread_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    if password is None:
        password = ""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_user(username, password):
    # Validate inputs
    if not username or not password:
        return False
    
    # Trim whitespace and normalize
    username = str(username).strip()
    password = str(password).strip()
    
    # Validate after trimming
    if not username or not password:
        return False
    
    conn = get_connection()
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        # Log error for debugging (can be removed later)
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def verify_user(username, password):
    # Validate inputs
    if not username or not password:
        return None
    
    # Trim whitespace and normalize to match stored values
    username = str(username).strip()
    password = str(password).strip()
    
    # Validate after trimming
    if not username or not password:
        return None
    
    conn = get_connection()
    c = conn.cursor()
    try:
        # First check if username exists (for better error messages)
        c.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user_row = c.fetchone()
        
        if not user_row:
            return None
        
        user_id, stored_hash = user_row
        hashed_pw = hash_password(password)
        
        # Compare hashes
        if hashed_pw == stored_hash:
            return user_id
        else:
            return None
    except Exception as e:
        # Log error for debugging (can be removed later)
        print(f"Error verifying user: {e}")
        return None
    finally:
        conn.close()

def link_thread_to_user(user_id, thread_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT OR IGNORE INTO user_threads (user_id, thread_id) VALUES (?, ?)', (user_id, str(thread_id)))
        conn.commit()
    finally:
        conn.close()

def get_user_threads(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT thread_id FROM user_threads WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    threads = [row[0] for row in c.fetchall()]
    conn.close()
    return threads

def delete_thread(user_id, thread_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        # We only delete the link between user and thread. 
        # The actual thread data in checkpoints might remain but won't be accessible to the user.
        c.execute('DELETE FROM user_threads WHERE user_id = ? AND thread_id = ?', (user_id, str(thread_id)))
        conn.commit()
        return c.rowcount > 0
    finally:
        conn.close()

def create_session(user_id):
    token = str(uuid.uuid4())
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO sessions (token, user_id) VALUES (?, ?)', (token, user_id))
        conn.commit()
        return token
    finally:
        conn.close()

def get_user_from_session(token):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT user_id FROM sessions WHERE token = ?', (token,))
        result = c.fetchone()
        if result:
            return result[0]
        return None
    finally:
        conn.close()

def delete_session(token):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()
    finally:
        conn.close()

def get_username(user_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def get_user_by_username(username):
    """Get user info by username - useful for debugging"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT id, username, password FROM users WHERE username = ?', (username.strip(),))
        result = c.fetchone()
        if result:
            return {'id': result[0], 'username': result[1], 'password_hash': result[2]}
        return None
    finally:
        conn.close()

def verify_user_debug(username, password):
    """Debug version of verify_user that returns detailed info"""
    if not username or not password:
        return {'success': False, 'reason': 'empty_input'}
    
    username = username.strip()
    password = password.strip()
    
    if not username or not password:
        return {'success': False, 'reason': 'empty_after_trim'}
    
    conn = get_connection()
    c = conn.cursor()
    try:
        # First check if user exists
        c.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
        user_row = c.fetchone()
        
        if not user_row:
            return {'success': False, 'reason': 'user_not_found', 'searched_username': username}
        
        user_id, db_username, db_password = user_row
        hashed_pw = hash_password(password)
        
        if hashed_pw == db_password:
            return {'success': True, 'user_id': user_id}
        else:
            return {
                'success': False, 
                'reason': 'password_mismatch',
                'user_id': user_id,
                'db_username': db_username,
                'input_hash': hashed_pw[:20] + '...',
                'stored_hash': db_password[:20] + '...'
            }
    finally:
        conn.close()
