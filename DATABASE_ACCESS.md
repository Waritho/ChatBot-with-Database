# Database Access Guide

This guide shows you different ways to access and view your SQLite database.

## 📊 Quick View Script

The easiest way to view your database is using the provided Python script:

```bash
python view_database.py
```

This will show you:
- All registered users (usernames, IDs, creation dates)
- Active sessions
- Chat threads per user
- Database structure and statistics

## 🗄️ Method 1: Python Script (Recommended)

**Run the database viewer:**
```bash
python view_database.py
```

This script displays a formatted view of all your database tables, including:
- **Users table**: All registered users with their IDs, usernames, and registration dates
- **Sessions table**: Active login sessions
- **User Threads table**: Chat threads linked to each user
- **Checkpoints table**: LangGraph conversation checkpoints (technical data)

## 🖥️ Method 2: SQLite Command Line

If you have SQLite installed, you can use the command line:

```bash
sqlite3 chatbot.db
```

Then run SQL queries:

```sql
-- View all users
SELECT * FROM users;

-- View users with readable format
SELECT id, username, created_at FROM users ORDER BY created_at DESC;

-- Count total users
SELECT COUNT(*) as total_users FROM users;

-- View active sessions
SELECT s.token, u.username, s.created_at 
FROM sessions s 
JOIN users u ON s.user_id = u.id 
ORDER BY s.created_at DESC;

-- Exit SQLite
.quit
```

## 🎨 Method 3: DB Browser for SQLite (GUI Tool)

1. **Download DB Browser for SQLite**: https://sqlitebrowser.org/
2. **Install** it on your system
3. **Open** the database file: `chatbot.db` (located in your project root)
4. **Browse** tables, run queries, and edit data visually

This is the easiest way for non-technical users!

## 🔍 Quick SQL Queries

### View All Registered Users
```sql
SELECT id, username, created_at FROM users ORDER BY created_at DESC;
```

### Find User by Username
```sql
SELECT * FROM users WHERE username = 'your_username';
```

### View All Active Sessions
```sql
SELECT u.username, s.token, s.created_at 
FROM sessions s 
JOIN users u ON s.user_id = u.id;
```

### View Chat Threads for a User
```sql
SELECT ut.thread_id, ut.created_at 
FROM user_threads ut 
WHERE ut.user_id = 1;  -- Replace 1 with actual user_id
```

### Delete a User (⚠️ Use with caution!)
```sql
DELETE FROM users WHERE username = 'username_to_delete';
```

## 📝 Database Schema

Your database contains these main tables:

1. **users** - Stores registered user accounts
   - `id` (Primary Key)
   - `username` (Unique)
   - `password` (Hashed)
   - `created_at` (Timestamp)

2. **sessions** - Stores active login sessions
   - `token` (Primary Key)
   - `user_id` (Foreign Key to users)
   - `created_at` (Timestamp)

3. **user_threads** - Links chat threads to users
   - `user_id` (Foreign Key to users)
   - `thread_id` (Chat thread identifier)
   - `created_at` (Timestamp)

4. **checkpoints** - LangGraph conversation state (technical)
   - Stores conversation history and AI state

5. **writes** - LangGraph write operations (technical)
   - Internal LangGraph data

## 🔐 Security Notes

⚠️ **Important**: 
- Passwords are stored as SHA-256 hashes (not reversible)
- Never share your database file publicly
- The database file is in the project root: `chatbot.db`

## 📍 Database Location

```
ChatBot 2/
└── chatbot.db          ← Your database file
    ├── chatbot.db-shm  ← SQLite temporary file
    └── chatbot.db-wal  ← SQLite temporary file
```

## 🛠️ Troubleshooting

**Can't find the database?**
- Make sure you're in the project root directory
- The database is created automatically when you first run the app
- Check the path: `C:\Users\shubh\Downloads\ChatBot 2\chatbot.db`

**Permission errors?**
- Close the Streamlit app before accessing the database
- Make sure no other program is using the database file

**Want to reset the database?**
⚠️ **Warning**: This will delete all users and data!
```bash
# Close the Streamlit app first, then:
rm chatbot.db chatbot.db-shm chatbot.db-wal  # On Windows: del chatbot.db*
```

