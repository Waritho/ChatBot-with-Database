#!/usr/bin/env python3
"""
Simple script to view the chatbot database contents
Run this script to see all registered users and other database information

Usage:
    python view_database.py

This will display:
- All registered users (usernames, IDs, registration dates)
- Active login sessions
- Chat threads per user
- Database statistics
"""

import sqlite3
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.database import DB_PATH, get_connection

def view_database():
    print("=" * 60)
    print("NEXUS AI - DATABASE VIEWER")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found at: {DB_PATH}")
        return
    
    print(f"\nDatabase Location: {DB_PATH}")
    print(f"Database Size: {os.path.getsize(DB_PATH) / 1024:.2f} KB\n")
    
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Get all table names
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        
        print(f"Found {len(tables)} table(s):\n")
        
        # View each table
        for (table_name,) in tables:
            print("-" * 60)
            print(f"TABLE: {table_name}")
            print("-" * 60)
            
            # Get table schema
            c.execute(f"PRAGMA table_info({table_name})")
            columns = c.fetchall()
            
            if columns:
                print("\nColumns:")
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_str = " (PRIMARY KEY)" if pk else ""
                    null_str = " NOT NULL" if not_null else ""
                    default_str = f" DEFAULT {default_val}" if default_val else ""
                    print(f"  - {col_name}: {col_type}{null_str}{default_str}{pk_str}")
            
            # Get all data from table
            c.execute(f"SELECT * FROM {table_name}")
            rows = c.fetchall()
            
            print(f"\nTotal Records: {len(rows)}\n")
            
            if rows:
                # Get column names
                column_names = [description[0] for description in c.description]
                
                # Print header
                print(" | ".join(column_names))
                print("-" * 60)
                
                # Print rows
                for row in rows:
                    # Format row data for display
                    formatted_row = []
                    for item in row:
                        if item is None:
                            formatted_row.append("NULL")
                        elif isinstance(item, str) and len(item) > 30:
                            formatted_row.append(item[:27] + "...")
                        else:
                            formatted_row.append(str(item))
                    print(" | ".join(formatted_row))
            else:
                print("(No records found)")
            
            print("\n")
        
        # Special summary for users table
        print("=" * 60)
        print("USER SUMMARY")
        print("=" * 60)
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        print(f"Total Registered Users: {user_count}\n")
        
        if user_count > 0:
            c.execute("SELECT id, username, created_at FROM users ORDER BY created_at DESC")
            users = c.fetchall()
            print("Registered Users:")
            for user_id, username, created_at in users:
                print(f"  - ID: {user_id} | Username: {username} | Created: {created_at}")
        
        # Session summary
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        c.execute("SELECT COUNT(*) FROM sessions")
        session_count = c.fetchone()[0]
        print(f"Active Sessions: {session_count}\n")
        
        if session_count > 0:
            c.execute("""
                SELECT s.token, s.user_id, u.username, s.created_at 
                FROM sessions s
                LEFT JOIN users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
            sessions = c.fetchall()
            print("Active Sessions:")
            for token, user_id, username, created_at in sessions:
                token_short = token[:8] + "..." if len(token) > 8 else token
                print(f"  - Token: {token_short} | User: {username} (ID: {user_id}) | Created: {created_at}")
        
        # Thread summary
        print("\n" + "=" * 60)
        print("THREAD SUMMARY")
        print("=" * 60)
        c.execute("SELECT COUNT(*) FROM user_threads")
        thread_count = c.fetchone()[0]
        print(f"Total Chat Threads: {thread_count}\n")
        
        if thread_count > 0:
            c.execute("""
                SELECT ut.user_id, u.username, COUNT(*) as thread_count
                FROM user_threads ut
                LEFT JOIN users u ON ut.user_id = u.id
                GROUP BY ut.user_id, u.username
                ORDER BY thread_count DESC
            """)
            user_threads = c.fetchall()
            print("Threads per User:")
            for user_id, username, count in user_threads:
                print(f"  - {username} (ID: {user_id}): {count} thread(s)")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print("View complete!")
    print("=" * 60)

if __name__ == "__main__":
    view_database()

