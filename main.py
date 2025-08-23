import mysql.connector
db = mysql.connector.connect(
    host = "localhost",
    user = "root" , #input("Enter your MySQL username: "),
    passwd = input("Enter your MySQL password: "),
    database = "workout" #input("Enter your MySQL database name: ")
)

cursor = db.cursor()

cursor.execute("SELECT DATABASE()")
print("Connected to:",cursor.fetchone()[0])

cursor.execute("Show tables;")
print("Tables:")
for table in cursor:
    for i in table:
        print(i)

def create_user(uname,passwd):
    cursor.execute(f"INSERT INTO users VALUES('{uname}', '{passwd}');")
    cursor.execute(f"CREATE TABLE {uname} (date DATE, exercise VARCHAR(255), sets INT, reps INT);")
    db.commit()

def login(uname,passwd):
    #if the given uname exists in the users table with the given passwd, the person can access their table with the given uname
    cursor.execute(f"SELECT * FROM users WHERE username = '{uname}' AND password = '{passwd}';")
    if cursor.fetchone() == None:
        print("Invalid credentials")
        return False
    else:
        cursor.execute(f"SELECT * FROM {uname};")
        return True

def add_data(uname,date,exercise,sets,reps):
    cursor.execute(f"INSERT INTO {uname} VALUES('{date}', '{exercise}', {sets}, {reps});")
    db.commit()
