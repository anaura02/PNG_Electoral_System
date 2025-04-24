from database.db_connection import execute_query

# Test user retrieval
users = execute_query("SELECT * FROM users")
print("Users:", users)

# Test candidates retrieval
candidates = execute_query("SELECT * FROM candidates WHERE province = 'East Sepik'")
print("Candidates in East Sepik:", candidates)