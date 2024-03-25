from pymongo import MongoClient
from bson.objectid import ObjectId  # For ObjectId to work

# Database connection
client = MongoClient('mongodb://localhost:27017/')
db = client[local_settings.DATABASE['name']]  # Connect to the database specified in local_settings

def is_valid_phone_number(number):
    # Check if the input is a string
    if not isinstance(number, str):
        return False

    # Check if the input consists of only digits
    if not number.isdigit():
        return False

    # Check if the length of the input is exactly 11 characters
    if len(number) != 11:
        return False

    return True

def is_valid_address(address):
    # Check if the input is a string
    if not isinstance(address, str):
        return False

    # Check if the input contains only alphanumeric characters
    if not address.isalnum():
        return False

    return True

def add_contact():
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
            print("Invalid address. Please enter a valid string without signs.")

    # Insert the contact document into the MongoDB collection
    db.contacts.insert_one(contact_doc)

    print(f"Contact '{first_name} {last_name}' added successfully!")

def display_contacts():
    print("All Contacts:")
    contacts = db.contacts.find()

    for contact in contacts:
        print(f"Name: {contact['first_name']} {contact['last_name']}")

        # Print phone numbers
        if 'phone_numbers' in contact:
            for phone_number in contact['phone_numbers']:
                print(f"   {phone_number['tag']}: {phone_number['number']}")

        # Print addresses
        if 'addresses' in contact:
            for address in contact['addresses']:
                print(f"   {address['tag']}: {address['address']}")

        print()

def search_contacts():
    keyword = input("Enter keyword to search: ")
    query = db.contacts.find({
        "$or": [
            {"first_name": {"$regex": keyword, "$options": "i"}},  # Case-insensitive regex match for first name
            {"last_name": {"$regex": keyword, "$options": "i"}}   # Case-insensitive regex match for last name
        ]
    })

    search_results = list(query)
    if search_results:
        print("Search Results:")
        for idx, contact in enumerate(search_results, start=1):
            print(f"{idx}. {contact['first_name']} {contact['last_name']}")

        while True:
            choice = input(
                "Enter the number of the contact to view details (or 'all' to show all results, or 'exit' to return "
                "to the main menu): ")
            if choice.lower() == 'exit':
                return
            elif choice.lower() == 'all':
                display_contacts()
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(search_results):
                selected_contact = search_results[int(choice) - 1]

                # Print selected contact details
                print(f"\nDetails for {selected_contact['first_name']} {selected_contact['last_name']}:")

                # Print phone numbers
                if 'phone_numbers' in selected_contact:
                    for phone_number in selected_contact['phone_numbers']:
                        print(f"   {phone_number['tag']}: {phone_number['number']}")

                # Print addresses
                if 'addresses' in selected_contact:
                    for address in selected_contact['addresses']:
                        print(f"   {address['tag']}: {address['address']}")

                return
            else:
                print("Invalid choice. Please try again.")
    else:
        print("No matching contacts found.")

if __name__ == "__main__":
    try:
        # No need to create tables since MongoDB is schema-less

        while True:
            print("\nMenu:")
            print("1. Add Contact")
            print("2. Display Contacts")
            print("3. Search Contacts")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                add_contact()
            elif choice == "2":
                display_contacts()
            elif choice == "3":
                search_contacts()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")

    except Exception as error:
        print("Error:", error)
    finally:
        # Close the database connection
        client.close()
        print("Database connection is closed")