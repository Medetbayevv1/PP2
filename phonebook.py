# phonebook.py
# ============================================================
# PhoneBook Application  —  backed by PostgreSQL
# ============================================================
# This is the MAIN file. Run it with:   python phonebook.py
#
# WHAT IT DOES:
#   Shows a menu, lets the user pick an action (add, search,
#   update, delete), runs the matching SQL, and repeats.
# ============================================================

import csv                         # Built-in Python module to read CSV files
from connect import get_connection, create_table  # Our helper functions


# ─────────────────────────────────────────────
#  HELPER — run SQL safely
# ─────────────────────────────────────────────

def run_query(sql, params=None, fetch=False):
    """
    Central function to execute ANY SQL statement.

    WHY do we have this?
        So every function below doesn't repeat the
        connect → cursor → execute → commit → close dance.

    PARAMETERS:
        sql    → the SQL string, e.g. "SELECT * FROM phonebook"
        params → a tuple of values to safely insert into the SQL
                 (prevents SQL Injection attacks!)
        fetch  → True if we want rows back (SELECT), False otherwise
    """
    conn = get_connection()
    if conn is None:
        return []

    result = []
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)     # params replaces %s placeholders safely

        if fetch:
            result = cursor.fetchall()  # Get all returned rows
        else:
            conn.commit()               # Save INSERT / UPDATE / DELETE changes

    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()                 # Undo changes if an error occurred

    finally:
        cursor.close()
        conn.close()

    return result


# ─────────────────────────────────────────────
#  1. INSERT from CSV file
# ─────────────────────────────────────────────

def insert_from_csv(filepath="contacts.csv"):
    """
    Reads a CSV file and inserts every row into the phonebook table.

    CSV FORMAT expected:
        first_name,last_name,phone
        Alice,Smith,+1-800-111-2222
        ...

    ON CONFLICT DO NOTHING:
        If a phone number already exists, skip that row instead of crashing.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)     # Reads rows as dictionaries using header names
            count = 0
            for row in reader:
                run_query(
                    """
                    INSERT INTO phonebook (first_name, last_name, phone)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (phone) DO NOTHING;
                    """,
                    (row["first_name"], row["last_name"], row["phone"])
                )
                count += 1
        print(f"[OK] Imported {count} rows from '{filepath}'.")

    except FileNotFoundError:
        print(f"[ERROR] File '{filepath}' not found. Make sure it's in the same folder.")


# ─────────────────────────────────────────────
#  2. INSERT from console (user types values)
# ─────────────────────────────────────────────

def insert_from_console():
    """
    Asks the user to type a contact's details, then inserts it.
    """
    print("\n--- Add a new contact ---")
    first = input("First name : ").strip()
    last  = input("Last name  : ").strip()   # Optional — can be empty
    phone = input("Phone      : ").strip()

    if not first or not phone:
        print("[WARN] First name and phone are required.")
        return

    run_query(
        """
        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone) DO NOTHING;
        """,
        (first, last or None, phone)   # Store None (NULL) if last name is empty
    )
    print(f"[OK] Contact '{first} {last}' added.")


# ─────────────────────────────────────────────
#  3. UPDATE a contact
# ─────────────────────────────────────────────

def update_contact():
    """
    Lets the user update either the name OR the phone of a contact.
    The user searches by phone number to find the right person.
    """
    print("\n--- Update a contact ---")
    phone = input("Enter the CURRENT phone number of the contact to update: ").strip()

    # Check if the contact exists first
    rows = run_query(
        "SELECT id, first_name, last_name, phone FROM phonebook WHERE phone = %s;",
        (phone,), fetch=True
    )
    if not rows:
        print("[WARN] No contact found with that phone number.")
        return

    # Show what we found
    row = rows[0]
    print(f"Found: ID={row[0]}  Name={row[1]} {row[2]}  Phone={row[3]}")

    print("What do you want to update?")
    print("  1. First name")
    print("  2. Phone number")
    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        new_val = input("New first name: ").strip()
        run_query(
            "UPDATE phonebook SET first_name = %s WHERE phone = %s;",
            (new_val, phone)
        )
        print("[OK] First name updated.")

    elif choice == "2":
        new_val = input("New phone number: ").strip()
        run_query(
            "UPDATE phonebook SET phone = %s WHERE phone = %s;",
            (new_val, phone)
        )
        print("[OK] Phone number updated.")

    else:
        print("[WARN] Invalid choice.")


# ─────────────────────────────────────────────
#  4. QUERY / SEARCH contacts
# ─────────────────────────────────────────────

def print_rows(rows):
    """Helper to display rows nicely in a table."""
    if not rows:
        print("  (no results found)")
        return
    print(f"\n  {'ID':<5} {'First Name':<15} {'Last Name':<15} {'Phone':<20}")
    print("  " + "-" * 57)
    for r in rows:
        print(f"  {r[0]:<5} {r[1]:<15} {str(r[2] or ''):<15} {r[3]:<20}")
    print()


def search_contacts():
    """
    Offers multiple ways to search the phonebook:
      1. Show ALL contacts
      2. Search by name (partial match using ILIKE — case-insensitive LIKE)
      3. Search by phone prefix
    """
    print("\n--- Search contacts ---")
    print("  1. Show ALL contacts")
    print("  2. Search by name")
    print("  3. Search by phone prefix")
    choice = input("Choice (1/2/3): ").strip()

    if choice == "1":
        rows = run_query(
            "SELECT id, first_name, last_name, phone FROM phonebook ORDER BY first_name;",
            fetch=True
        )
        print_rows(rows)

    elif choice == "2":
        name = input("Enter name (or part of it): ").strip()
        # ILIKE is PostgreSQL's case-insensitive LIKE
        # % is a wildcard: %alice% matches 'Alice', 'ALICE', 'malice', etc.
        rows = run_query(
            """
            SELECT id, first_name, last_name, phone
            FROM phonebook
            WHERE first_name ILIKE %s OR last_name ILIKE %s
            ORDER BY first_name;
            """,
            (f"%{name}%", f"%{name}%"), fetch=True
        )
        print_rows(rows)

    elif choice == "3":
        prefix = input("Enter phone prefix (e.g. +1 or +7-700): ").strip()
        rows = run_query(
            """
            SELECT id, first_name, last_name, phone
            FROM phonebook
            WHERE phone LIKE %s
            ORDER BY phone;
            """,
            (f"{prefix}%",), fetch=True    # Matches anything starting with prefix
        )
        print_rows(rows)

    else:
        print("[WARN] Invalid choice.")


# ─────────────────────────────────────────────
#  5. DELETE a contact
# ─────────────────────────────────────────────

def delete_contact():
    """
    Deletes a contact by either username (first name) or phone number.
    """
    print("\n--- Delete a contact ---")
    print("  1. Delete by first name")
    print("  2. Delete by phone number")
    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        name = input("First name to delete: ").strip()
        # Check how many rows match before deleting
        rows = run_query(
            "SELECT id, first_name, last_name, phone FROM phonebook WHERE first_name ILIKE %s;",
            (name,), fetch=True
        )
        if not rows:
            print("[WARN] No contact found with that name.")
            return
        print(f"These contacts will be deleted:")
        print_rows(rows)
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            run_query(
                "DELETE FROM phonebook WHERE first_name ILIKE %s;",
                (name,)
            )
            print("[OK] Contact(s) deleted.")
        else:
            print("[CANCELLED] No changes made.")

    elif choice == "2":
        phone = input("Phone number to delete: ").strip()
        rows = run_query(
            "SELECT id, first_name, last_name, phone FROM phonebook WHERE phone = %s;",
            (phone,), fetch=True
        )
        if not rows:
            print("[WARN] No contact found with that phone number.")
            return
        print(f"This contact will be deleted:")
        print_rows(rows)
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            run_query(
                "DELETE FROM phonebook WHERE phone = %s;",
                (phone,)
            )
            print("[OK] Contact deleted.")
        else:
            print("[CANCELLED] No changes made.")

    else:
        print("[WARN] Invalid choice.")


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def main():
    """
    Entry point. Creates the table if needed, then shows the menu in a loop.
    """
    print("=" * 50)
    print("      PHONEBOOK  —  PostgreSQL Edition")
    print("=" * 50)

    # Step 1: Make sure the table exists
    create_table()

    # Step 2: Loop forever until user picks Exit
    while True:
        print("\nMAIN MENU")
        print("  1. Import contacts from CSV file")
        print("  2. Add a contact (manual entry)")
        print("  3. Update a contact")
        print("  4. Search / View contacts")
        print("  5. Delete a contact")
        print("  0. Exit")

        choice = input("\nYour choice: ").strip()

        if   choice == "1": insert_from_csv()
        elif choice == "2": insert_from_console()
        elif choice == "3": update_contact()
        elif choice == "4": search_contacts()
        elif choice == "5": delete_contact()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("[WARN] Please enter a number from the menu.")


# Run main() only when this script is executed directly
if __name__ == "__main__":
    main()