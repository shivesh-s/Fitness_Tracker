import mysql.connector

UI = """
Welcome to the Workout Tracker!
Please choose an option:

 +---------------------------------------------+
| OPTION   | DESCRIPTION                        |
 +---------------------------------------------+
| cr_user   | Create a new user                 |
| add       | Add workout data                  |
| edit      | Edit workout data                 |
| rm_user   | Remove a user                     |
| BMI       | Calculate BMI                     |
| PR        | Log Personal Record               |
| oneRM     | Calculate One-Rep Max             |
| exit (e)  | Exit the program                  |
 +---------------------------------------------+
"""

#* conecting to mysql
db = mysql.connector.connect(
    host = "localhost",
    user = "root" , #input("Enter your MySQL username: "),
    passwd = input("Enter your MySQL password: "),
    database = "workout" #input("Enter your MySQL database name: ")
)

cursor = db.cursor(buffered=True)

#* printing working database and its tables
cursor.execute("SELECT DATABASE()")
print("Connected to:",cursor.fetchone()[0])

cursor.execute("Show tables;")
r = cursor.fetchall()
print("\n------------\nTables:\n------------")
if r == []:
    
    cursor.execute("CREATE TABLE users (username VARCHAR(14), password VARCHAR(10), bench_1rm int(3), weight decimal(4,1), height decimal(3,2),age int(2), gender char(1));")
    print("users table created")
else:
    for i in r:
        print(i[0])
    print("------------\n")
#* Defining some necessary functions
def create_user(uname,passwd):
    '''creates a new user in the database'''
    rm = input("Your previous bench press 1RM in KG (leave blank if none): ")
    if rm == "":
        rm = 0
    weight = float(input("Enter your weight in KG: "))
    height = float(input("Enter your height in metres: "))
    gender = input("Enter your gender (M/F): ").upper()
    age = int(input("Enter your age: "))
    cursor.execute(f"INSERT INTO users VALUES('{uname}', '{passwd}',{int(rm)},{weight},{height},{age},'{gender}');")
    cursor.execute(f"CREATE TABLE {uname} (date DATE, exercise VARCHAR(255), sets INT, reps INT, PR BOOLEAN not null);")
    db.commit()
    return [uname,passwd]

def login(uname,passwd):
    '''Accepts two strings as arguments and checks if the user exists in the database, returns True if it does and False if it doesn't'''
    cursor.execute(f"SELECT * FROM users WHERE username = '{uname}' AND password = '{passwd}';")
    r = cursor.fetchone()
    if r == None:
        print("Invalid credentials")
        return [0]
    else:
        # cursor.execute(f"SELECT * FROM {uname};")
        return [1,uname,passwd]

def add_data(uname,pwd):
    '''Accepts four strings as arguments and adds data to the user's table'''
    date = input("Enter the date (YYYY-MM-DD): ")
    exercise = input("Enter the exercise name: ")
    sets,reps = int(input("Enter the number of sets: ")), int(input("Enter the number of reps: "))
    cursor.execute(f"INSERT INTO {uname} VALUES('{date}', '{exercise}', {sets}, {reps},0);")
    db.commit()
    print("Data added successfully.")

def edit(uname,pwd):
    '''Accepts four strings as arguments and edits the data in the user's table'''
    date = input("Enter the date (YYYY-MM-DD) of the entry you want to edit: ")
    exercise = input("Enter the new exercise name: ")
    sets,reps  = int(input("Enter the new number of sets: ")), int(input("Enter the new number of reps: "))
    cursor.execute(f"UPDATE {uname} SET exercise = '{exercise}', sets = {sets}, reps = {reps} WHERE date = '{date}';")
    db.commit()
    print("Entry updated successfully.")


def BMI(user,pwd):
    cursor.execute(f"SELECT weight, height FROM users WHERE username = '{user}' AND password = '{pwd}';")
    r = cursor.fetchone()
    weight, height = r[0], r[1]
    BMI = weight/((height/100)**2)
    print(f"Your BMI is: {round(BMI,2)}")

def oneRM(uname,pwd):
    weight = input("Enter the weight: ")
    reps = input("Enter the reps: ")
    rm = round(weight * (36/(37-reps),2))
    cursor.execute(f"UPDATE users SET bench_1rm = {rm} WHERE username = '{uname}';") 
    return rm
    

def PR_logger(uname,pwd):
    date = input("Enter the date (YYYY-MM-DD): ")
    exercise = input("Enter the exercise name: ")
    sets,reps = int(input("Enter the number of sets: ")), int(input("Enter the number of reps: "))
    cursor.execute(f"SELECT * FROM {uname} WHERE exercise = '{exercise}' AND PR = 1;")
    if cursor.fetchone() != None:
        cursor.execute(f"UPDATE {uname} SET date = '{date}', exercise = '{exercise}', sets = {sets}, reps = {reps} WHERE PR = 1;")
        db.commit()
    else:
        cursor.execute(f"INSERT INTO {uname} VALUES('{date}', '{exercise}', {sets}, {reps});")
    db.commit()

def admin():
    admin_pass = input("Enter admin password: ")
    if admin_pass == "admin123":  # Example admin password
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        print("All users in the database:")
        for user in users:
            print(user)
    else:
        print("Invalid admin password.")
    
    def remove_user(uname,passwd):
        '''Accepts two strings as arguments and removes the user from the database'''
        cursor.execute(f"DELETE FROM users WHERE username = '{uname}' AND password = '{passwd}';")
        cursor.execute(f"DROP TABLE {uname};")
        print("User removed successfully.")
        db.commit()


run = True
functions = {
    "cr_user" : create_user,
    "add" : add_data,
    "edit" : edit,
    "bmi" : BMI,
    "pr" : PR_logger,
    "onerm" : oneRM,
    }


ut = input("Are you a new user? (y/n): ").lower()
uname,passwd = input("Enter your username: "),input("Enter your password: ")

if ut == "n" or ut == "no":
    log = login(uname,passwd)
    if log[0]:
        print("Login successful")
        
    else:
        print("Login failed. Exiting...")
        run = False
else:
    unp = create_user(uname,passwd)
    print("User created successfully. Please you will be automatically logged in now.")
    log = login(unp[0],unp[1])
    if log[0]:
        print("Login successful")
        uname,passwd = log[1],log[2]
    else:
        print("Login failed. Exiting...")
        run = False

# UI
while run:
    print(UI)
    ch = input("Enter the name of the function: ").lower() 
    if ch == "e" or ch == "exit":
        run = False
    elif ch == "admin":
        admin()
    else:
        functions[ch](uname,passwd)