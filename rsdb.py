"""
Connect to Database
"""
import mysql.connector


class Rsdb:
    config = {
        "user": "root",
        "password": "rootpassword",
        "host": "localhost",
        "database": "rs-database",
        "port": "3308"
    }

    isConnected = False

    def check_exist_table(self):
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'user'")
        result = cursor.fetchone()
        if result:
            print("Table 'user' exists")
        else:
            print("Table does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE user (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), score VARCHAR(255))")
            self.connection.commit()
            print("Table created")

        cursor.execute("SHOW TABLES LIKE 'vanue'")
        result = cursor.fetchone()
        if result:
            print("Table 'vanue' exists")
        else:
            print("Table does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE vanue (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), score INT, latitude DOUBLE PRECISION, longitude DOUBLE PRECISION, link VARCHAR(255))")
            self.connection.commit()
            print("Table created")

        cursor.execute("SHOW TABLES LIKE 'review'")
        result = cursor.fetchone()
        if result:
            print("Table 'review' exists")
        else:
            print("Table does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE review (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, vanue_id INT, score INT, time DOUBLE PRECISION, comment VARCHAR(255), link VARCHAR(255), review INT, FOREIGN KEY (user_id) REFERENCES user(id), FOREIGN KEY (vanue_id) REFERENCES vanue(id))")
            self.connection.commit()
            print("Table created")

        cursor.execute("SHOW TABLES LIKE 'category'")
        result = cursor.fetchone()
        if result:
            print("Table 'category' exists")
        else:
            print("Table does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE category (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
            self.connection.commit()
            print("Table created")

        cursor.execute("SHOW TABLES LIKE 'vanue_category'")
        result = cursor.fetchone()
        if result:
            print("Table 'vanue_category' exists")
        else:
            print("Table does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE vanue_category (id INT AUTO_INCREMENT PRIMARY KEY, vanue_id INT, category_id INT, FOREIGN KEY (vanue_id) REFERENCES vanue(id), FOREIGN KEY (category_id) REFERENCES category(id))")
            self.connection.commit()
            print("Table created")
        # close cursor
        cursor.close()

    def get_connection(self):
        return self.connection

    def get_is_connected(self):
        return self.isConnected

    def close_connection(self):
        self.connection.close()
        print("MySQL connection is closed")

    def __init__(self):
        self.connection = mysql.connector.connect(**self.config)
        if self.connection.is_connected():
            self.isConnected = True
            print("Connected to MySQL database")

            # check if table exists
            self.check_exist_table()
        else:
            self.isConnected = False
            print("Failed to connect to MySQL database")
