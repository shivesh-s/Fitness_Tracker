import mysql.connector

#* conecting to mysql
db = mysql.connector.connect(
    host = "localhost",
    user = "root" , #input("Enter your MySQL username: "),
    passwd = input("Enter your MySQL password: "),
    database = "workout" #input("Enter your MySQL database name: ")
)

cursor = db.cursor()

#* pinting working database and its tables
cursor.execute("SELECT DATABASE()")
print("Connected to:",cursor.fetchone()[0])

cursor.execute("Show tables;")
print("Tables:")
for table in cursor:
    for i in table:
        print(i)

#* Defining some necessary functions
def create_user(uname,passwd):
    '''Accepts two strings as arguments and creates a new user in the database'''
    cursor.execute(f"INSERT INTO users VALUES('{uname}', '{passwd}');")
    cursor.execute(f"CREATE TABLE {uname} (date DATE, exercise VARCHAR(255), sets INT, reps INT);")
    db.commit()

def login(uname,passwd):
    '''Accepts two strings as arguments and checks if the user exists in the database, returns True if it does and False if it doesn't'''
    cursor.execute(f"SELECT * FROM users WHERE username = '{uname}' AND password = '{passwd}';")
    if cursor.fetchone() == None:
        print("Invalid credentials")
        return False
    else:
        # cursor.execute(f"SELECT * FROM {uname};")
        return True

def add_data(uname,date,exercise,sets,reps):
    '''Accepts four strings as arguments and adds data to the user's table'''
    cursor.execute(f"INSERT INTO {uname} VALUES('{date}', '{exercise}', {sets}, {reps});")
    db.commit()
