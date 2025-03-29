from datetime import datetime, timedelta
import sqlite3

databasePath = "library.db"

def get_db_connection():
    conn = sqlite3.connect(databasePath)
    conn.row_factory = sqlite3.Row
    return conn

def find_item(title):
    conn = get_db_connection()
    cur = conn.cursor()

    # set up and execute query
    query = "SELECT * FROM Item WHERE title LIKE ? AND status != ?"
    titleString = f"%{title}%"
    cur.execute(query, (titleString, "FutureItem"))

    # fetch all matching rows
    results = cur.fetchall()

    conn.close()
    return results    

# returns true if item is borrowed successsfully
def borrow_item(user_id, item_id, due_date):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT status FROM Item WHERE ItemID = ?", (item_id,))
    status = cur.fetchone()
    if status and status[0] == "Available": 

        # insert a new loan 
        cur.execute(
            "INSERT INTO Loan (due, UserID, ItemID) VALUES (?, ?, ?)",
            (due_date, user_id, item_id)
        )
        conn.commit()
        print(f"Item borrowed successfully. This item is due on {due_date}")
        conn.close
        return True
    else:
        print("Item is not available for borrowing.")
        conn.close()
        return False

def return_item(user_id, item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Loan WHERE UserID = ? AND ItemID = ?", (user_id, item_id))
    if cur.rowcount > 0:
        print("Item returned successfully!")
        conn.commit()
    else:
        print("You don't have this item borrowed!")
    conn.close()
    return

def donate_item(title, type, author, duration, url):
    conn = get_db_connection()
    cur = conn.cursor()

    # First insert into item the generic attributes
    cur.execute(
        "INSERT INTO Item (title, type, author, status) VALUES (?, ?, ?, ?)",
        (title, type, author, "FutureItem")
    )

    # If it is a subclass, insert into subclass's table
    item_id = cur.lastrowid

    if type == 'CD':
        cur.execute(
            "INSERT INTO CD (ItemID, duration) VALUES (?, ?)",
            (item_id, duration)
            )
    elif type == 'OnlineItem':
        cur.execute(
            "INSERT INTO OnlineItem (ItemID, url) VALUES (?, ?)",
            (item_id, url)
            )
        
    conn.commit()
    conn.close()


# returns a list of Event tuples
def find_event(type):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Event WHERE type LIKE ?", (f"%{type}%",))
    events = cur.fetchall()
    return events

def register_event(userID, EventID):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Attends (userID, EventID) VALUES (?, ?)",
        (userID, EventID)
    )
    conn.commit()
    conn.close()

def volunteer(name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Personnel (name, position, salary) VALUES (?, ?, ?, ?)",
        (name, "Volunteer", 0)
    )
    conn.commit()
    conn.close()

def ask_for_help(userID, message):
    conn = get_db_connection()
    cur = conn.cursor()

    # Find the email of the current user. 
    cur.execute(
        "SELECT email FROM User WHERE userID = ?", (userID,)
    )
    email = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO HelpRequests (email, message) VALUES (?, ?)",
        (email, message)
    )
    conn.commit()
    conn.close()

def create_user(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO User (email) VALUES (?)", (email,)
    )
    user_id = cur.lastrowid
    print(f"Account successfully created. Your user ID is {user_id}")
    conn.commit()
    conn.close()

def check_valid(user_id):

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT userID FROM User WHERE userID == ?", (user_id,)
    )
    result = cur.fetchone()
    conn.close()

    return result is not None

def print_loans(): 
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Loan"
    )
    loans = cur.fetchall()
    for loan in loans:
        print(dict(loan))

# Main application loop with command line interface
def main():
    # print_loans()
    conn = sqlite3.connect("library.db")

    # Starting menu
    while True:
        print("1. Log in\n2. Sign up\n3. Quit")
        choice = int(input("Enter your choice: ").strip())

        if choice == 1: 
            cur_id = int(input("Enter your user ID: ").strip())
            if check_valid(cur_id):
                print("You are now logged in!")
                break
            else:
                print("Invalid ID")
        elif choice == 2: 
            email = input("Enter your email: ")
            create_user(email)
            break

        elif choice == 3: 
            print("Exiting the application")
            return 
        
        else:
            print("Invalid choice, please try again: ")
        

    # Main menu
    while True: 
        print("\nLibrary Application Menu:")
        print("1. Find an Item")
        print("2. Borrow an Item")
        print("3. Return a Borrowed Item")
        print("4. Donate an Item")
        print("5. Find an Event")
        print("6. Register for an Event")
        print("7. Volunteer for the Library")
        print("8. Ask for Help from a Librarian")
        print("9. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            title = input("Enter the title (or part of it) to search for: ")
            items = find_item(title)
            if items:
                print("Items found:")
                for item in items:
                    print(dict(item))
            else:
                print("No matching items found.")

        elif choice == "2":
            try:
                item_id = int(input("Enter the Item ID to borrow: "))

                # calculate the due date 
                due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d");
                
                borrow_item(cur_id, item_id, due_date)
            except ValueError:
                print("Invalid input. Please enter numeric values for IDs.")

        elif choice == "3":
            try:
                item_id = int(input("Enter the Item ID to return: "))
                return_item(cur_id, item_id)
            except ValueError:
                print("Invalid input. Please enter numeric values for IDs.")

        elif choice == "4":
            title = input("Enter the title of the donated item: ")
            type_ = input("Enter the type of the donated item (e.g., CD, OnlineItem, Book): ")
            author = input("Enter the author (or publisher): ")
            # For subclass attributes, ask for additional details based on type.
            if type_ == 'CD':
                duration = input("Enter the duration (in minutes): ")
                donate_item(title, type_, author, duration, None)
            elif type_ == 'OnlineItem':
                url = input("Enter the URL: ")
                donate_item(title, type_, author, None, url)
            else:
                # For types that don't require extra subclass info, pass None.
                donate_item(title, type_, author, None, None)
            print("Donation recorded successfully.")

        elif choice == "5":
            event_type = input("Enter the event type (or name) to search for: ")
            events = find_event(event_type)
            if events:
                print("Events found:")
                for event in events:
                    print(dict(event))
            else:
                print("No matching events found.")

        elif choice == "6":
            try:
                EventID = int(input("Enter the Event ID to register for: "))
                register_event(cur_id, EventID)
                print("Registered for the event successfully.")
            except ValueError:
                print("Invalid input. Please enter numeric values for IDs.")

        elif choice == "7":
            name = input("Enter your name: ")
            volunteer(name)
            print("Thank you for volunteering!")

        elif choice == "8":
            try:
                message = input("Enter your help request message: ")
                ask_for_help(cur_id, message)
                print("Your help request has been submitted.")
            except ValueError:
                print("Invalid input. Please enter a valid User ID.")

        elif choice == "9":
            print("Exiting the application")
            break

        else:
            print("Invalid choice. Please try again.")
        


if __name__ == '__main__':
    main()