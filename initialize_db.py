from database.db_connection import execute_query

def setup_database():
    # Read SQL file
    with open('database/db_setup.sql', 'r') as file:
        sql_commands = file.read()
    
    # Execute each command
    for command in sql_commands.split(';'):
        if command.strip():
            execute_query(command)
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()