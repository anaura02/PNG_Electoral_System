import psycopg2
from psycopg2.extras import DictCursor, Json
import os
import json

# Register JSON adapter
psycopg2.extensions.register_adapter(dict, Json)

# Database connection parameters
DB_CONFIG = {
    'dbname': 'election_db',
    'user': 'postgres',
    'password': 'JkHaFaCaRnCtAc2002',
    'host': 'localhost',
    'port': '5432'
}

def create_connection():
    """Create a database connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        if params:
            try:
                cursor.execute(query, params)
            except Exception as e:
                print(f"Error executing query: {e}")
                print(f"Query: {query}")
                print(f"Params: {params}")
                print(f"Param types: {[type(p) for p in params if p is not None]}")
                raise
        else:
            cursor.execute(query)
            
        # Check if the query is a SELECT query
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Error executing query: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_dict_query(query, params=None):
    """Execute a query and return results as dictionaries"""
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if not conn:
            return None
        
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Check if the query is a SELECT query
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Error executing query: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def initialize_database():
    """Initialize the database with tables if they don't exist"""
    # SQL to create tables
    create_tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            province VARCHAR(50) NOT NULL,
            district VARCHAR(50) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'voter',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            party VARCHAR(100) NOT NULL,
            district VARCHAR(50) NOT NULL,
            bio TEXT,
            photo BYTEA,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS votes (
            vote_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            candidate_id INTEGER REFERENCES candidates(candidate_id),
            preference INTEGER NOT NULL CHECK (preference IN (1, 2, 3)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, preference)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            key VARCHAR(50) PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Create each table
        for create_table_sql in create_tables_sql:
            cursor.execute(create_table_sql)
            
        conn.commit()
        print("Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def initialize_system_settings():
    """Initialize system settings if they don't exist"""
    default_settings = {
        'voting_status': 'open',  # 'open' or 'closed'
        'system_name': 'PNG Electoral System',
        'admin_contact': 'admin@pngelection.gov.pg'
    }
    
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Check if settings exist
        cursor.execute("SELECT COUNT(*) FROM system_settings")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insert default settings
            for key, value in default_settings.items():
                # Convert value to string if it's not already
                if isinstance(value, dict):
                    value = json.dumps(value)
                
                cursor.execute(
                    "INSERT INTO system_settings (key, value) VALUES (%s, %s)",
                    (key, value)
                )
                
            conn.commit()
            print("System settings initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"Error initializing system settings: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()