import psycopg2
from psycopg2.extras import RealDictCursor
import time

# while True:
#     try:
#         # conn = psycopg2.connect(host, database, user, password)
#         conn = psycopg2.connect(host='localhost', database='fastapi_db',
#         user = 'postgres', password = 'password123', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection is succesfull")
#         break
#     except Exception as err:
#         print("Connection was failed")
#         print(err)
#         time.sleep(2)
