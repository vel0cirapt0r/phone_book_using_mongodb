from pymongo import MongoClient

import local_settings

import re


class DatabaseManager:
    def __init__(self, database_name, host, port):
        self.database_name = database_name
        self.host = host
        self.port = port
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]

    def close_connection(self):
        self.client.close()


def is_valid_phone_number(number):
    return isinstance(number, str) and number.isdigit() and len(number) == 11


def is_valid_address(address):
    pattern = r'^[a-zA-Z][a-zA-Z0-9 -]*$'
    return bool(re.match(pattern, address))


def add_contact(db):
    """add a new contact to the database"""
    try:
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")

        contact_doc = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_numbers": [],
            "addresses": []
        }

        while True:
            number = input("Enter phone number (leave blank to skip): ")
            if not number:
                break
            tag = input("Enter phone number tag (e.g., home, work): ")
            if is_valid_phone_number(number):
                contact_doc["phone_numbers"].append({"tag": tag, "number": number})
            else:
                print("Invalid phone number. Please enter a valid 11-digit integer.")

        while True:
            address = input("Enter address (leave blank to skip): ")
            if not address:
                break
            tag = input("Enter address tag (e.g., home, work): ")
            if is_valid_address(address):
                contact_doc["addresses"].append({"tag": tag, "address": address})
            else:
                print("Invalid address. Please enter a valid address containing only letters, numbers, spaces, "
                      "and hyphens, and starting with a letter.")

        db.db.contacts.insert_one(contact_doc)  # Access the contacts collection from the database object
        print(f"Contact '{first_name} {last_name}' added successfully!")
    except Exception as e:
        print("Error adding contact:", e)


def display_contacts(db):
    try:
        print("All Contacts:")
        contacts = db.db.contacts.find()  # Access the contacts collection from the database object

        for contact in contacts:
            print(f"Name: {contact['first_name']} {contact['last_name']}")
            if 'addresses' in contact:
                for address in contact['addresses']:
                    print(f"   {address['tag']}: {address['address']}")

            if 'phone_numbers' in contact:
                for phone_number in contact['phone_numbers']:
                    print(f"   {phone_number['tag']}: {phone_number['number']}")

    except Exception as e:
        print("Error displaying contacts:", e)


def search_contacts(db):
    try:
        keyword = input("Enter keyword to search: ")
        query = db.db.contacts.find({
            "$or": [
                {"first_name": {"$regex": keyword, "$options": "i"}},
                {"last_name": {"$regex": keyword, "$options": "i"}}
            ]
        })

        search_results = list(query)
        if search_results:
            print("Search Results:")
            for idx, contact in enumerate(search_results, start=1):
                print(f"{idx}. {contact['first_name']} {contact['last_name']}")
            while True:
                choice = input(
                    "Enter the number of the contact to view details (or 'all' to show all results, or 'exit' to "
                    "return to the main menu): ")
                if choice.lower() == 'exit':
                    return
                elif choice.lower() == 'all':
                    display_contacts(db)
                    return
                elif choice.isdigit() and 1 <= int(choice) <= len(search_results):
                    selected_contact = search_results[int(choice) - 1]
                    print(f"\nDetails for {selected_contact['first_name']} {selected_contact['last_name']}:")
                    if 'addresses' in selected_contact:
                        for address in selected_contact['addresses']:
                            print(f"   {address['tag']}: {address['address']}")
                    if 'phone_numbers' in selected_contact:
                        for phone_number in selected_contact['phone_numbers']:
                            print(f"   {phone_number['tag']}: {phone_number['number']}")
                    return
                else:
                    print("Invalid choice. Please try again.")
        else:
            print("No matching contacts found.")

    except Exception as e:
        print("Error searching contacts:", e)


if __name__ == "__main__":
    db_manager = None  # Initialize db_manager variable
    try:
        # Database connection
        db_manager = DatabaseManager(local_settings.DATABASE['name'],
                                     local_settings.DATABASE['host'],
                                     local_settings.DATABASE['port'])
        while True:
            print("\nMenu:")
            print("1. Add Contact")
            print("2. Display Contacts")
            print("3. Search Contacts")
            print("4. Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                add_contact(db_manager)
            elif choice == "2":
                display_contacts(db_manager)
            elif choice == "3":
                search_contacts(db_manager)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")

    except Exception as error:
        print("Error:", error)
    finally:
        if db_manager:
            db_manager.close_connection()
            print("Database connection is closed")
