import threading
import mysql.connector
import random
from datetime import date

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "rootpassword",
    "database": "project_db"
}

def insert_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "INSERT INTO ClimateData (location, record_date, temperature, precipitation, humidity) VALUES (%s,%s,%s,%s,%s)"
    data = ("TestCity", date.today(), random.uniform(15, 35), random.uniform(0, 20), random.uniform(40, 80))
    cursor.execute(query, data)
    conn.commit()
    conn.close()

def select_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ClimateData WHERE temperature > 20")
    rows = cursor.fetchall()
    print("Select Query Result:", rows[:5])
    conn.close()

def update_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE ClimateData SET humidity=75 WHERE location='Toronto'")
    conn.commit()
    conn.close()

threads = []
for func in [insert_data, select_data, update_data]:
    t = threading.Thread(target=func)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Concurrent queries executed successfully!")