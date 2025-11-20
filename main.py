import mysql.connector

print(
    '''
-------------------------------------------------------------
 █▀▀ ▀█▀ ▀█▀ █▀█ █▀▀ █▀▀ █▀▀   ▀█▀ █▀▄ █▀█ █▀▀ █ █ █▀▀ █▀▄
 █▀▀  █   █  █ █ █▀▀ ▀▀█ ▀▀█    █  █▀▄ █▀█ █   █▀▄ █▀▀ █▀▄   
 ▀   ▀▀▀  ▀  ▀ ▀ ▀▀▀ ▀▀▀ ▀▀▀    ▀  ▀ ▀ ▀ ▀ ▀▀▀ ▀ ▀ ▀▀▀ ▀ ▀ v1.0
--------- www.github.com/shivesh-s/fitness_tracker ----------                                                          
'''
)


UI = """

Please choose an option:

 +--------- + ---------------------------------+
| OPTION    | DESCRIPTION                       |
 +--------- + ---------------------------------+
| cr_user   | Create a new user                 |
| add       | Add workout data                  |
| edit      | Edit workout data                 |
| rm_user   | Remove current user               |
| bmi       | Calculate BMI                     |
| pr        | Log Personal Record               |
| onerm     | Calculate 1 Rep Max for benchpress|
| view      | View workout entries              |
| admin     | Admin Dashboard                   |
| exit (e)  | Exit the program                  |
 +--------- + ---------------------------------+
"""

#* -------------------------------------------------------------
#* Database Connection
#* -------------------------------------------------------------
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd='root',
        database="workout"
    )
    cursor = db.cursor(buffered=True)
except mysql.connector.Error as err:
    print("Database connection failed:", err)
    exit()

#* -------------------------------------------------------------
#* Check or Create Database Table
#* -------------------------------------------------------------
try:
    cursor.execute("SELECT DATABASE()")
    print("Connected to:", cursor.fetchone()[0])

    cursor.execute("SHOW TABLES;")
    r = cursor.fetchall()
    print("\n +------------\n| Tables:     |\n +------------")
    if not r:
        # users table stores account and basic physical info
        cursor.execute("""
        CREATE TABLE users (
            username VARCHAR(14) PRIMARY KEY,
            password VARCHAR(10),
            bench_1rm INT(3),
            weight DECIMAL(4,1),
            height DECIMAL(4,2),
            age INT(2),
            gender CHAR(1)
        );
        """)
        print("users table created.")
    else:
        for i in r:
            l = len(i[0])
            print("| "+i[0] + " " * (12 - l) + "|")
        print(" +-----------+\n")
except mysql.connector.Error as err:
    print("Error during initialization:", err)
    exit()

#* -------------------------------------------------------------
#* FUNCTIONS
#* -------------------------------------------------------------

def create_user(uname, passwd):
    """Create a new user with basic info and their own workout table."""
    try:
        print("\n"+"---"*7 + 'Creating new user' + "---"*7)
        rm = input("Your previous bench press 1RM in KG (leave blank if none): ")
        rm = int(rm) if rm.strip() else 0
        weight = float(input("Enter your weight in KG: "))
        height = float(input("Enter your height in metres: "))
        gender = input("Enter your gender (M/F): ").upper()
        age = int(input("Enter your age: "))

        # Add user into users table
        cursor.execute(
            "INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (uname, passwd, rm, weight, height, age, gender)
        )

        # Create a separate table for each user’s workouts
        cursor.execute(f"""
        CREATE TABLE {uname} (
            date DATE,
            exercise VARCHAR(255),
            sets INT,
            reps INT,
            weight DECIMAL(5,2),
            PR BOOLEAN NOT NULL DEFAULT 0
        );
        """)
        db.commit()
        print("---"*8 + 'User Created' + "---"*8 +"\n")
        print("User created successfully.")
        return [uname, passwd]
    except mysql.connector.Error as err:
        print("Error creating user:", err)
        db.rollback()


def login(uname, passwd):
    """Login a user; returns [1, uname, passwd] if success, else [0]."""
    try:
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (uname, passwd))
        r = cursor.fetchone()
        if not r:
            print("Invalid credentials.")
            return [0]
        return [1, uname, passwd]
    except mysql.connector.Error as err:
        print("Login error:", err)
        return [0]


def add_data(uname, pwd):
    """Add a new workout entry (date, exercise, sets, reps) for a user."""
    try:
        date = input("Enter the date (YYYY-MM-DD): ")
        exercise = input("Enter the exercise name: ")
        sets = int(input("Enter sets: "))
        reps = int(input("Enter reps: "))
        weight = float(input("Enter weight used (kg): "))
        cursor.execute(f"INSERT INTO {uname} VALUES(%s, %s, %s, %s, %s, 0)", (date, exercise, sets, reps,weight))
        db.commit()
        print("Data added successfully.")
    except Exception as e:
        print("Error adding data:", e)
        db.rollback()


# -------------------------------------------------------------
def edit(uname, pwd):
    """Edit a specific entry in the user’s workout log based on date."""
    try:
        date = input("Enter the date (YYYY-MM-DD) to edit: ")
        exercise = input("Enter new exercise name: ")
        sets = int(input("Enter new sets: "))
        reps = int(input("Enter new reps: "))
        weight = float(input("Enter new weight used (kg): "))
        cursor.execute(f"UPDATE {uname} SET exercise=%s, sets=%s, reps=%s, weight=%s WHERE date=%s", (exercise, sets, reps,weight, date))
        db.commit()
        print("Entry updated successfully.")
    except mysql.connector.Error as err:
        print("Error updating entry:", err)
        db.rollback()


def BMI(user, pwd):
    """Calculate and print BMI using weight and height."""
    try:
        cursor.execute("SELECT weight, height FROM users WHERE username=%s AND password=%s", (user, pwd))
        r = cursor.fetchone()
        if not r:
            print("User not found.")
            return
        weight, height = r
        BMI = weight / (height ** 2)
        print(f"Your BMI is: {round(BMI, 2)}")
    except Exception as e:
        print("Error calculating BMI:", e)


def oneRM(uname, pwd):
    """Calculate 1-rep max using the Epley formula and update user data."""
    try:
        weight = float(input("Enter the weight you benched (kg): "))
        reps = int(input("Enter the reps: "))
        rm = round(weight * (36 / (37 - reps)), 2)
        cursor.execute("UPDATE users SET bench_1rm=%s WHERE username=%s", (rm, uname))
        db.commit()
        print(f"Your estimated 1RM is {rm} kg")
        return rm
    except Exception as e:
        print("Error calculating 1RM:", e)
        db.rollback()


def PR_logger(uname, pwd):
    """Log or update a Personal Record entry for a specific exercise."""
    try:
        date = input("Enter the date (YYYY-MM-DD): ")
        exercise = input("Enter the exercise name: ")
        sets, reps = int(input("Sets: ")), int(input("Reps: "))
        weight = float(input("Weight used (kg): "))

        # If PR exists for that exercise, update it. Else, create new.
        cursor.execute(f"SELECT * FROM {uname} WHERE exercise=%s AND PR=1", (exercise,))
        if cursor.fetchone():
            cursor.execute(f"UPDATE {uname} SET date=%s, sets=%s, reps=%s , weight=%s WHERE exercise=%s AND PR=1", (date, sets, reps, weight, exercise))
        else:
            cursor.execute(f"INSERT INTO {uname} VALUES(%s, %s, %s, %s,%s, 1)", (date, exercise, sets, reps, weight))
        db.commit()
        print("PR logged successfully.")
    except Exception as e:
        print("Error logging PR:", e)
        db.rollback()


def remove_user(uname, passwd):
    """Delete a user and their workout table from the database."""
    try:
        cursor.execute("DELETE FROM users WHERE username=%s AND password=%s", (uname, passwd))
        cursor.execute(f"DROP TABLE IF EXISTS {uname}")
        db.commit()
        print("User removed successfully.")
        global run
        run=False
    except mysql.connector.Error as err:
        print("Error removing user:", err)
        db.rollback()

def view(uname, pwd):
    """View all workout entries for the user as a table."""
    try:
        cursor.execute(f"SELECT * FROM {uname}")
        rows = cursor.fetchall()
        print("\n"+" "+"---"*9 + 'Workout Entries' + "---"*8)
        print("| Date       | Exercise           | Sets | Reps | Weight (kg) | PR |")
        print("+" + "-"*11 + "+" + "-"*20 + "+" + "-"*6 + "+" + "-"*6 + "+" + "-"*13 + "+" + "-"*4 + "+")
        for row in rows:
            date, exercise, sets, reps, weight, pr = row
            pr_str = "Yes" if pr else "No"
            print(f"| {date} | {exercise:<18} | {sets:<4} | {reps:<4} | {weight:<11} | {pr_str:<2} |")
        print(" "+"---"*9 + 'End of Entries-' + "---"*8 +"\n")
    except mysql.connector.Error as err:
        print("Error viewing entries:", err)

def admin():
    """Admin dashboard — manage all users, delete users, reset PRs."""
    admin_pass = input("> Enter admin password: ")
    if admin_pass != "admin123":
        print("Invalid admin password.")
        return
    
    while True:
        print(r"""
 +---------------------------------------------+
|                 ADMIN OPTIONS                 |
 +---------------------------------------------+
| 1. View all users                             |
| 2. Remove a user                              |
| 3. Reset a user's PRs                         |
| 4. Exit admin                                 |
 +---------------------------------------------+
    """)
        choice = input("> Select option: ").strip()
        if choice == "1":
            cursor.execute("SELECT username, bench_1rm, weight, height, age, gender FROM users")
            for u in cursor.fetchall():
                for i in u:
                    k = len(str(i))
                    if u[0] == i:
                        print("|" + str(i) + " "*(8 - k),end=" | ")
                    else:
                        print(i, end=" | ")
                print()
        elif choice == "2":
            uname = input("> Enter username to remove: ")
            if uname == "admin":
                print("Cannot remove admin user.")
                continue
            cursor.execute("SELECT * FROM users WHERE username=%s", (uname,))
            if not cursor.fetchone():
                print("User not found.")
                continue
            cursor.execute("DELETE FROM users WHERE username=%s", (uname,))
            cursor.execute(f"DROP TABLE IF EXISTS {uname}")
            db.commit()
            print(f"User {uname} removed.")
        elif choice == "3":
            uname = input("Enter username to reset PRs: ")
            cursor.execute(f"UPDATE {uname} SET PR=0")
            db.commit()
            print("All PRs reset for", uname)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")


#* -------------------------------------------------------------
#* MAIN PROGRAM LOOP
#* -------------------------------------------------------------
functions = {
    "cr_user": create_user,
    "add": add_data,
    "edit": edit,
    "bmi": BMI,
    "pr": PR_logger,
    "onerm": oneRM,
    "view": view,
    "rm_user": remove_user
}

run = True
ut = input("> Are you a new user? (y/n): ").lower()
uname = input("> Enter your username: ")
passwd = input("> Enter your password: ")

# user login or creation
if ut in ("n", "no"):
    log = login(uname, passwd)
    if log[0]:
        print("Login successful.")
    else:
        print("Login failed. Exiting...")
        run = False
else:
    unp = create_user(uname, passwd)
    log = login(unp[0], unp[1])
    if log[0]:
        print("Login successful.")
        uname, passwd = log[1], log[2]
    else:
        print("Login failed. Exiting...")
        run = False

# main menu loop
print("Welcome to the Workout Tracker!")
while run:
    print(UI)
    ch = input("> Enter option: ").lower()
    if ch in ("e", "exit"):
        run = False
    elif ch == "admin":
        admin()
    elif ch in functions:
        functions[ch](uname, passwd)
    else:
        print("Invalid option.")

cursor.close()
db.close()
print("Exiting Workout Tracker. Goodbye!")