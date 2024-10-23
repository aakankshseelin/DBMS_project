import streamlit as st
import mysql.connector

# Sample user database (username: password)
user_credentials = {
    "admin": "password123",
    "user1": "password456"
}

# Function to check login credentials
def check_login(username, password):
    if username in user_credentials and user_credentials[username] == password:
        return True
    else:
        return False

# Function to display the login page
def login_page():
    st.title("Login to PES Library Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Welcome, {username}!")
            # Set a flag to rerun the script using query parameters
            st.query_params = {"logged_in": "true"}
        else:
            st.error("Invalid username or password")

# Function to connect to the MySQL database and fetch data for a specified table
def fetch_data(table_name):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="lib_mgmt"
        )
        cursor = connection.cursor()

        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        data = cursor.fetchall()

        connection.close()

        st.table(data)

    except mysql.connector.Error as error:
        st.error(f"Error: {error}")

# Function to call the Cust_Membership function in MySQL
def call_cust_membership_function(customer_id):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="lib_mgmt"
        )
        cursor = connection.cursor()

        query = f"SELECT Cust_Membership({customer_id})"
        cursor.execute(query)
        data = cursor.fetchall()

        connection.close()

        return data[0][0] if data else "No data found"

    except mysql.connector.Error as error:
        return f"Error: {error}"

def fetch_admin_data():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="lib_mgmt"
        )
        cursor = connection.cursor()

        query = "SELECT CONCAT(First_Name, ' ', Last_Name) AS Full_Name, Email FROM Administrators"
        cursor.execute(query)
        data = cursor.fetchall()

        connection.close()

        st.table(data)

    except mysql.connector.Error as error:
        st.error(f"Error: {error}")

def update_book_availability(isbn, action):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="lib_mgmt"
        )
        cursor = connection.cursor()

        if action == "checkout":
            cursor.execute("SELECT * FROM books WHERE ISBN = %s AND Availability = 'In stock'", (isbn,))
            book = cursor.fetchone()

            if book:
                cursor.execute("UPDATE books SET Availability = 'Checked out' WHERE ISBN = %s", (isbn,))
                connection.commit()
                st.success(f"Book with ISBN {isbn} has been checked out.")
            else:
                st.error(f"Book with ISBN {isbn} is not available for check-out.")

        elif action == "return":
            cursor.execute("SELECT * FROM books WHERE ISBN = %s AND Availability = 'Checked out'", (isbn,))
            book = cursor.fetchone()

            if book:
                cursor.execute("UPDATE books SET Availability = 'In stock' WHERE ISBN = %s", (isbn,))
                connection.commit()
                st.success(f"Book with ISBN {isbn} has been returned.")
            else:
                st.error(f"Book with ISBN {isbn} is not marked as checked out.")

        else:
            st.error("Invalid action specified.")

        connection.close()  

    except mysql.connector.Error as error:
        st.error(f"Error: {error}")

def add_new_book(isbn, title, author, category):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="lib_mgmt"
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM books WHERE ISBN = %s", (isbn,))
        existing_book = cursor.fetchone()

        if existing_book:
            st.warning(f"Book with ISBN {isbn} already exists in the database.")
        else:
            cursor.execute("INSERT INTO books (ISBN, Title, Author, Category, Availability) VALUES (%s, %s, %s, %s, 'In stock')", (isbn, title, author, category))
            connection.commit()
            st.success(f"Book with ISBN {isbn} has been added to the database.")

        connection.close()

    except mysql.connector.Error as error:
        st.error(f"Error: {error}")

def remove_book(isbn):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="lib_mgmt"
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM books WHERE ISBN = %s", (isbn,))
        existing_book = cursor.fetchone()

        if existing_book:
            cursor.execute("DELETE FROM books WHERE ISBN = %s", (isbn,))
            connection.commit()
            st.success(f"Book with ISBN {isbn} has been removed from the database.")
        else:
            st.warning(f"Book with ISBN {isbn} does not exist in the database.")

        connection.close()

    except mysql.connector.Error as error:
        st.error(f"Error: {error}")

# Main portal function with the original app content
def main_portal():
    st.title("Welcome to PES Library Portal")
    st.write(f"Logged in as: {st.session_state['username']}")

    if st.button("Check available books"):
        st.subheader("Viewing Books table")
        fetch_data("books")

    st.subheader("View Membership Status")
    customer_id = st.number_input("Enter Customer ID", min_value=1, max_value=10, step=1, format="%d")

    if st.button("View Membership"):
        result = call_cust_membership_function(customer_id)
        st.write(f"Membership Type: {result}")

    if st.button("View Admin Data"):
        st.subheader("Viewing full name and emails of Admins")
        fetch_admin_data()

    isbn = st.text_input("Enter ISBN")
    if st.button("Check Out"):
        update_book_availability(isbn, "checkout")
    if st.button("Return"):
        update_book_availability(isbn, "return")

    st.subheader("Add a New Book")
    new_isbn = st.text_input("New ISBN")
    new_title = st.text_input("Title")
    new_author = st.text_input("Author")
    new_category = st.text_input("Category")
    if st.button("Add New Book"):
        add_new_book(new_isbn, new_title, new_author, new_category)

    st.subheader("Remove an Existing Book")
    remove_isbn = st.text_input("ISBN of the Book to Remove")
    if st.button("Remove Book"):
        remove_book(remove_isbn)

# Logic to control app flow
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_portal()
else:
    login_page()
