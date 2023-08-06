import mysql.connector
from mysql.connector import Error
import os


# Connecting to database using environment variables
def connect_to_mysql():
    conn = mysql.connector.connect()
    h=os.environ.get('DB_HOST')
    u=os.environ.get('DB_USER')
    p=os.environ.get('DB_PASSWORD')
    d=os.environ.get('DB_DATABASE')
    # print(h,u,p,d)
    try :
       conn = mysql.connector.connect(
        host=h,
        user=u,
        password=p,
        database=d,
        port=11111
        )
       # testing database connection
       if conn.is_connected():
           info=conn.get_server_info()
           print("Connected to MySql server version",info)
           cursor = conn.cursor()
           cursor.execute("select database();")
           record = cursor.fetchone()
           print("You're connected to database: ", record)
    except Error as e:
        print("Error while connecting to mysql",e)

    return conn