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
            print("Table 'user' exists", end='\r')
        else:
            print("Table 'user' does not exist", end='\r')
            # create table
            cursor.execute('''
                CREATE TABLE user (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    name VARCHAR(255), 
                    link LONGTEXT, 
                    reviews INT, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
                ''')
            self.connection.commit()
            print("Table 'user' created", end='\r')

        cursor.execute("SHOW TABLES LIKE 'venue'")
        result = cursor.fetchone()
        if result:
            print("Table 'venue' exists", end='\r')
        else:
            print("Table 'venue' does not exist", end='\r')
            # create table
            cursor.execute('''
                CREATE TABLE venue (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    name VARCHAR(255), 
                    score DOUBLE PRECISION DEFAULT NULL, 
                    latitude DOUBLE PRECISION DEFAULT NULL, 
                    longitude DOUBLE PRECISION DEFAULT NULL,
                    link LONGTEXT DEFAULT NULL,
                    location LONGTEXT DEFAULT NULL,
                    province VARCHAR(255) DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)                
                ''')
            self.connection.commit()
            print("Table 'venue' created", end='\r')

        cursor.execute("SHOW TABLES LIKE 'review'")
        result = cursor.fetchone()
        if result:
            print("Table 'review' exists", end='\r')
        else:
            print("Table 'review' does not exist", end='\r')
            # create table
            cursor.execute('''
                CREATE TABLE review (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    user_id INT, 
                    venue_id INT, 
                    score INT, 
                    time DOUBLE PRECISION, 
                    comment LONGTEXT, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(id), 
                    FOREIGN KEY (venue_id) REFERENCES venue(id))
                ''')
            self.connection.commit()
            print("Table 'review' created", end='\r')

        cursor.execute("SHOW TABLES LIKE 'category'")
        result = cursor.fetchone()
        if result:
            print("Table 'category' exists", end='\r')
        else:
            print("Table 'category' does not exist", end='\r')
            # create table
            cursor.execute('''
                CREATE TABLE category (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
                ''')
            self.connection.commit()
            print("Table 'category' created", end='\r')

        cursor.execute("SHOW TABLES LIKE 'venue_category'")
        result = cursor.fetchone()
        if result:
            print("Table 'venue_category' exists", end='\r')
        else:
            print("Table 'venue_category' does not exist", end='\r')
            # create table
            cursor.execute('''
                CREATE TABLE venue_category (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    venue_id INT, 
                    category_id INT, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (venue_id) REFERENCES venue(id), 
                    FOREIGN KEY (category_id) REFERENCES category(id))
                    ''')
            self.connection.commit()
            print("Table 'venue_category' created", end='\r')
        # close cursor
        cursor.close()

    def is_exist_venue_url(self, url):
        cursor = self.connection.cursor()
        sql_select = "SELECT id FROM venue WHERE link = %s"
        val = (url,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        cursor.close()
        if result:
            return True
        else:
            return False

    def is_exist_venue(self, name):
        cursor = self.connection.cursor()
        sql_select = "SELECT id FROM venue WHERE name = %s"
        val = (name,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return False

    def get_users(self):
        cursor = self.connection.cursor()
        sql_select = "SELECT * FROM user"
        cursor.execute(sql_select)
        users = cursor.fetchall()
        cursor.close()
        return users

    def get_venue_category(self, venue_id):
        cursor = self.connection.cursor()
        sql_select = "SELECT category_id FROM venue_category WHERE venue_id = %s"
        val = (venue_id,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        category_id = result[0]

        sql_select = "SELECT name FROM category WHERE id = %s"
        val = (category_id,)
        cursor.execute(sql_select, val)
        category_name = cursor.fetchone()
        cursor.close()
        return category_name[0]

    def get_venue_data(self, venue_id):
        cursor = self.connection.cursor()
        sql_select = "SELECT * FROM venue WHERE id = %s"
        val = (venue_id,)
        cursor.execute(sql_select, val)
        score = cursor.fetchone()
        cursor.close()
        return score

    def get_connection(self):
        return self.connection

    def get_is_connected(self):
        return self.isConnected

    def close_connection(self):
        self.connection.close()
        print("MySQL connection is closed", end='\r')

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

    def insert_venue(self, name, score, latitude, longitude, link, venue_location):
        cursor = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM venue WHERE name = %s"
        val = (name,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        if result:
            venue_id = result[0]
            sql_update = "UPDATE venue SET score = %s, latitude = %s, longitude = %s, link = %s, location = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
            val = (score, latitude, longitude, link, venue_location, venue_id)
            cursor.execute(sql_update, val)
            self.connection.commit()
            cursor.fetchone()
            cursor.close()
            return venue_id
        else:
            # insert data
            sql_insert = "INSERT INTO venue (name, score, latitude, longitude, link, location) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, score, latitude, longitude, link, venue_location)
            cursor.execute(sql_insert, val)
            self.connection.commit()
            val = (name,)
            cursor.execute(sql_select, val)
            result = cursor.fetchone()
            self.connection.commit()
            cursor.close()
            return result[0]

    def insert_review(self, user_id, venue_id, score, time, comment):
        cursor = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM review WHERE user_id = %s AND venue_id = %s"
        val = (user_id, venue_id)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        if result:
            review_id = result[0]
            sql_update = "UPDATE review SET score = %s, comment = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
            val = (score, comment, review_id)
            cursor.execute(sql_update, val)
            self.connection.commit()
            cursor.fetchone()
            cursor.close()
            return review_id
        else:
            # insert data
            sql_insert = "INSERT INTO review (user_id, venue_id, score, time, comment) VALUES (%s, %s, %s, %s, %s)"
            val = (user_id, venue_id, score, time, comment)
            cursor.execute(sql_insert, val)
            self.connection.commit()

            val = (user_id, venue_id)
            cursor.execute(sql_select, val)
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def insert_category(self, name):
        cursor = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM category WHERE name = %s"
        val = (name,)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        if result:
            cursor.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO category (name) VALUES (%s)"
            val = (name,)
            cursor.execute(sql_insert, val)
            self.connection.commit()
            val = (name,)
            cursor.execute(sql_select, val)
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def insert_venue_category(self, venue_id, category_id):
        cursor = self.connection.cursor()
        # check exist data
        sql_select = "SELECT id FROM venue_category WHERE venue_id = %s AND category_id = %s"
        val = (venue_id, category_id)
        cursor.execute(sql_select, val)
        result = cursor.fetchone()
        if result:
            cursor.close()
            return result[0]
        else:
            # insert data
            sql_insert = "INSERT INTO venue_category (venue_id, category_id) VALUES (%s, %s)"
            val = (venue_id, category_id)
            cursor.execute(sql_insert, val)
            self.connection.commit()
            val = (venue_id, category_id)
            cursor.execute(sql_select, val)
            result = cursor.fetchone()
            cursor.close()
            return result[0]

    def drop_all_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "DROP TABLE review, venue_category, user, venue, category")
        cursor.close()
        print("All tables dropped", end='\r')

    def __init__(self):
        self.connection = mysql.connector.connect(**self.config)
        if self.connection.is_connected():
            self.isConnected = True
            print("Connected to MySQL database", end='\r')

            # check if table exists
            self.check_exist_table()
        else:
            self.isConnected = False
            print("Failed to connect to MySQL database", end='\r')
