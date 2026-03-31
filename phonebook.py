import psycopg2
from connect import get_connection


def load_sql():
    conn = get_connection()
    cur = conn.cursor()
    for file in ["functions.sql", "procedures.sql"]:
        with open(file) as f:
            cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()


def search(pattern):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()


def upsert(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s);", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Done.")


def bulk_insert(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL bulk_insert(%s::TEXT[][]);", (data,))
    conn.commit()
    cur.execute("SELECT * FROM invalid_entries;")
    invalid = cur.fetchall()
    cur.close()
    conn.close()
    if invalid:
        print("Invalid phones:")
        for row in invalid:
            print(" ", row)
    else:
        print("All inserted.")


def paged(limit, offset):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paged(%s, %s);", (limit, offset))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()


def delete(value, by):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s, %s);", (value, by))
    conn.commit()
    cur.close()
    conn.close()
    print("Deleted.")


load_sql()

while True:
    print("\n1.Search  2.Add/Update  3.Bulk  4.Page  5.Delete  0.Exit")
    c = input("Choice: ")

    if c == "1":
        search(input("Pattern: "))
    elif c == "2":
        upsert(input("Name: "), input("Phone: "))
    elif c == "3":
        data = []
        print("Enter name,phone — empty line to stop:")
        while True:
            line = input().strip()
            if not line:
                break
            n, p = line.split(",")
            data.append([n.strip(), p.strip()])
        bulk_insert(data)
    elif c == "4":
        paged(int(input("Limit: ")), int(input("Offset: ")))
    elif c == "5":
        delete(input("Value: "), input("By name or phone: "))
    elif c == "0":
        break