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
            print("Table 'user' does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE user (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), link LONGTEXT, reviews INT)")
            self.connection.commit()
            print("Table 'user' created")

        cursor.execute("SHOW TABLES LIKE 'venue'")
        result = cursor.fetchone()
        if result:
            print("Table 'venue' exists")
        else:
            print("Table 'venue' does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE venue (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), score DOUBLE PRECISION, latitude DOUBLE PRECISION, longitude DOUBLE PRECISION, link LONGTEXT)")
            self.connection.commit()
            print("Table 'venue' created")

        cursor.execute("SHOW TABLES LIKE 'review'")
        result = cursor.fetchone()
        if result:
            print("Table 'review' exists")
        else:
            print("Table 'review' does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE review (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, venue_id INT, score INT, time DOUBLE PRECISION, comment LONGTEXT, FOREIGN KEY (user_id) REFERENCES user(id), FOREIGN KEY (venue_id) REFERENCES venue(id))")
            self.connection.commit()
            print("Table 'review' created")

        cursor.execute("SHOW TABLES LIKE 'category'")
        result = cursor.fetchone()
        if result:
            print("Table 'category' exists")
        else:
            print("Table 'category' does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE category (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
            self.connection.commit()
            print("Table 'category' created")

        cursor.execute("SHOW TABLES LIKE 'venue_category'")
        result = cursor.fetchone()
        if result:
            print("Table 'venue_category' exists")
        else:
            print("Table 'venue_category' does not exist")
            # create table
            cursor.execute(
                "CREATE TABLE venue_category (id INT AUTO_INCREMENT PRIMARY KEY, venue_id INT, category_id INT, FOREIGN KEY (venue_id) REFERENCES venue(id), FOREIGN KEY (category_id) REFERENCES category(id))")
            self.connection.commit()
            print("Table 'venue_category' created")
        # close cursor
        cursor.close()

    def is_exist_venue(self, name):
        cursor = self.connection.cursor()
        sql_select = "SELECT id FROM venue WHERE name = %s"
        val = (name,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        cursor.close()
        if result:
            return True
        else:
            return False

    def get_connection(self):
        return self.connection

    def get_is_connected(self):
        return self.isConnected

    def close_connection(self):
        self.connection.close()
        print("MySQL connection is closed")

    def insert_user(self, name, link, review):
        cursor = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM user WHERE name = %s"
        val = (name,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        if result:
            cursor.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO user (name, link, reviews) VALUES (%s, %s, %s)"
            val = (name, link, review)
            cursor.execute(sql_insert, val)
            self.connection.commit()
            val = (name,)
            cursor.execute(sql_select, val)
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def insert_venue(self, name, score, latitude, longitude, link):
        cursor = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM venue WHERE name = %s"
        val = (name,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        if result:
            cursor.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO venue (name, score, latitude, longitude, link) VALUES (%s, %s, %s, %s, %s)"
            val = (name, score, latitude, longitude, link)
            cursor.execute(sql_insert, val)
            self.connection.commit()
            val = (name,)
            cursor.execute(sql_select, val)
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def insert_review(self, user_id, venue_id, score, time, comment):
        curser = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM review WHERE user_id = %s AND venue_id = %s"
        val = (user_id, venue_id)
        curser.execute(sql_select, val)
        result = curser.fetchone()
        if result:
            curser.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO review (user_id, venue_id, score, time, comment) VALUES (%s, %s, %s, %s, %s)"
            val = (user_id, venue_id, score, time, comment)
            curser.execute(sql_insert, val)
            self.connection.commit()
            val = (user_id, venue_id)
            curser.execute(sql_select, val)
            result = curser.fetchone()
            curser.close()
            return result[0]

    def insert_category(self, name):
        curser = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM category WHERE name = %s"
        val = (name,)
        curser.execute(sql_select, val)
        result = curser.fetchone()
        if result:
            curser.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO category (name) VALUES (%s)"
            val = (name,)
            curser.execute(sql_insert, val)
            self.connection.commit()
            val = (name,)
            curser.execute(sql_select, val)
            result = curser.fetchone()
            curser.close()
            return result[0]

    def insert_venue_category(self, venue_id, category_id):
        curser = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM venue_category WHERE venue_id = %s AND category_id = %s"
        val = (venue_id, category_id)
        curser.execute(sql_select, val)
        result = curser.fetchone()
        if result:
            curser.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO venue_category (venue_id, category_id) VALUES (%s, %s)"
            val = (venue_id, category_id)
            curser.execute(sql_insert, val)
            self.connection.commit()
            val = (venue_id, category_id)
            curser.execute(sql_select, val)
            result = curser.fetchone()
            curser.close()
            return result[0]

    def drop_all_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "DROP TABLE review, venue_category, user, venue, category")
        cursor.close()
        print("All tables dropped")

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
