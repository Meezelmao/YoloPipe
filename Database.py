import psycopg2


con = psycopg2.connect(
    database='postgres',
    user='postgres',
    password='Zx951357S',
    host="127.0.0.1",
    port="5432")

print("Database opened successfully")
cur = con.cursor()
cur.execute('''CREATE TABLE STUDENT  
     (ADMISSION INT PRIMARY KEY NOT NULL,
     NAME TEXT NOT NULL,
     AGE INT NOT NULL,
     COURSE CHAR(50),
     DEPARTMENT CHAR(50));''')
print('Table create succes')
con.commit()
con.close()