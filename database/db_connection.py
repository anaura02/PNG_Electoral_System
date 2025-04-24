import psycopg2
from psycopg2 import OperationalError

def create_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="election_db",
            user="postgres",
            password="JkHaFaCaRnCtAc2002",  
            port="5432"
        )
        return conn
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def execute_query(query, params=None):
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            conn.close()