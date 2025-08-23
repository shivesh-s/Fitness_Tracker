import mysql.connector

#* conecting to mysql
db = mysql.connector.connect(
    host = "localhost",
    user = "root" , #input("Enter your MySQL username: "),
    passwd = input("Enter your MySQL password: "),
    database = "workout" #input("Enter your MySQL database name: ")
)

cursor = db.cursor()

#* printing working database and its tables
cursor.execute("SELECT DATABASE()")
print("Connected to:",cursor.fetchone()[0])

cursor.execute("Show tables;")
print("Tables:")
for table in cursor:
    if "users" not in table:
        cursor.execute("CREATE TABLE users (username VARCHAR(14), password VARCHAR(10));")

#* Defining some necessary functions
def create_user():
    '''creates a new user in the database'''
    uname = input("Enter your username: ")
    passwd = input("Enter your password: ")
    cursor.execute(f"INSERT INTO users VALUES('{uname}', '{passwd}');")
    cursor.execute(f"CREATE TABLE {uname} (date DATE, exercise VARCHAR(255), sets INT, reps INT, PR BOOLEAN not null);")
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
    cursor.execute(f"INSERT INTO {uname} VALUES('{date}', '{exercise}', {sets}, {reps},0);")
    db.commit()
 
def edit(uname,date,exercise,sets,reps):
    '''Accepts four strings as arguments and edits the data in the user's table'''
    cursor.execute(f"UPDATE {uname} SET exercise = '{exercise}', sets = {sets}, reps = {reps} WHERE date = '{date}';")
    db.commit()

def remove_user(uname,passwd):
    '''Accepts two strings as arguments and removes the user from the database'''
    cursor.execute(f"DELETE FROM users WHERE username = '{uname}' AND password = '{passwd}';")
    cursor.execute(f"DROP TABLE {uname};")
    db.commit()

def BMI(weight, height):
    BMI = weight/((height/100)**2)
    return BMI

def PR_logger(uname,date,exercise,sets,reps):
    cursor.execute(f"SELECT * FROM {uname} WHERE exercise = '{exercise}' AND PR = 1;")
    if cursor.fetchone() != None:
        cursor.execute(f"UPDATE {uname} SET date = '{date}', exercise = '{exercise}', sets = {sets}, reps = {reps} WHERE PR = 1;")
        db.commit()
    else:
        cursor.execute(f"INSERT INTO {uname} VALUES('{date}', '{exercise}', {sets}, {reps});")
    db.commit()

def oneRM(uname,exercise):
    weight = input("Enter the weight: ")
    reps = input("Enter the reps: ")
    rm = round(weight * (36/(37-reps),2)) 
    return rm

# UI
