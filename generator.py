import sqlite3
from random import randint, choice
import os
from unidecode import unidecode

PASSWORD_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources.db')
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')

def connect_db(path):
    """Connect to the SQLite database."""
    return sqlite3.connect(path)

def create_table(data):
    """Create the information table if it doesn't exist."""
    with data:
        data.execute('''
            CREATE TABLE IF NOT EXISTS information (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, location TEXT, birthday TEXT,
                email TEXT, password TEXT
            )
        ''')

resources = connect_db(RESOURCES_PATH)
cursor_resources = resources.cursor()

data = connect_db(DATA_PATH)
create_table(data)
cursor_data = data.cursor()

def save_information(information):
    """Save generated information to the database."""
    formatted_info = (
        f'{information[0]} {information[1]}',
        f'{information[5]}, {information[6]}, {information[7]}, {information[8]}',
        f'{information[2]:02}/{information[3]:02}/{information[4]}',
        information[9], 
        information[10]
    )
    try:
        with data:
            data.execute('INSERT INTO information (name, location, birthday, email, password) VALUES (?, ?, ?, ?, ?)', formatted_info)
        print('Information saved successfully.')
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_random_value(table_name, condition=None, params=None):
    """Retrieve a random value from a specified table."""
    query = f"SELECT * FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    
    cursor_resources.execute(query, params or ())
    rows = cursor_resources.fetchall()
    return choice(rows) if rows else None

def generate_birthday():
    """Generate a random valid birthday."""
    month = randint(1, 12)
    day = randint(1, 28)
    year = randint(1995, 2012)
    return day, month, year

def generate_info(country=None):
    """Generate random personal information based on the provided country."""
    if not country:
        country = get_random_value('country')

    first_name = get_random_value('first_name', 'country_id = ?', (country[0],))
    last_name = get_random_value('last_name', 'country_id = ?', (country[0],))
    province = get_random_value('province', 'country_id = ?', (country[0],))
    district = get_random_value('district', 'province_id = ?', (province[0],))
    ward = get_random_value('ward', 'district_id = ?', (district[0],))
    birthday = generate_birthday()

    first_name = first_name[1] if first_name else "Unknown"
    last_name = last_name[1] if last_name else "Unknown"
    country = country[1] if country else "Unknown"
    province = province[1] if province else "Unknown"
    district = district[1] if district else "Unknown"
    ward = ward[1] if ward else "Unknown"

    email = f'{unidecode(first_name + last_name).lower().replace(" ", "")}{randint(1000,9999)}@gmail.com'
    password = ''.join(choice(PASSWORD_CHARS) for _ in range(15))

    return first_name, last_name, birthday[0], birthday[1], birthday[2], ward, district, province, country, email, password

def generate_single_information():
    """Generate and display a single set of information."""
    clear_screen()
    cursor_resources.execute('SELECT * FROM country;')
    countries = cursor_resources.fetchall()
    print('Generate Single Information\n')
    for i in countries:
        print(f'  [{i[0]:02}] {i[1]}')
    print('  [00] Random country')
    countries.append(None)

    try:
        option = int(input('\nChoose a country: '))
        if 0 <= option < len(countries):
            information = generate_info(countries[option - 1])
            print(f"\nGenerated Information for {information[8]}:\n")
            print(f'''Name: {information[0]} {information[1]}
Birthday: {information[2]:02}/{information[3]:02}/{information[4]}
Location: {information[5]} ward, {information[6]} district, {information[7]} province, {information[8]} country
Email: {information[9]}
Password: {information[10]}''')
            
            if input('\nSave this information? (y/n): ').strip().lower() == 'y':
                save_information(information)
        else:
            print("Invalid option! Please try again.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

def generate_multiple_information():
    """Generate and display multiple sets of information."""
    clear_screen()
    cursor_resources.execute('SELECT * FROM country;')
    countries = cursor_resources.fetchall()
    print('Generate Multiple Information\n')
    
    try:
        quantity = int(input('Enter quantity: '))
        print()
        for i in countries:
            print(f'  [{i[0]:02}] {i[1]}')
        print('  [00] Random country')
        countries.append(None)

        option = int(input('\nChoose a country: '))
        if 0 <= option < len(countries):
            informations = []
            for _ in range(quantity):
                information = generate_info(countries[option - 1])
                informations.append(information)
                print(f"\nGenerated Information for {information[8]}:\n")
                print(f'''
-----------------------------------------------
Name: {information[0]} {information[1]}
Birthday: {information[2]:02}/{information[3]:02}/{information[4]}
Location: {information[5]} ward, {information[6]} district, {information[7]} province, {information[8]} country
Email: {information[9]}
Password: {information[10]}\n''')

            if input('Save this information? (y/n): ').strip().lower() == 'y':
                for info in informations:
                    save_information(info)
        else:
            print("Invalid option! Please try again.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

def view_all_information():
    clear_screen()
    cursor_data.execute('SELECT id, name FROM information')
    records = cursor_data.fetchall()
    print('View All Information\n')
    if records:
        for i in records:
            print(f'ID: {i[0]}, Name: {i[1]}')
    else:
        print('No record found!')

def get_information_by_id():
    view_all_information()
    while True:
        try:
            search_id = int(input('\nEnter the ID: ').strip())
            cursor_data.execute('SELECT * FROM information WHERE id = ?', (search_id,))
            record = cursor_data.fetchone()
            if record:
                print(f'Name: {record[1]}\nLocation: {record[2]}\nBirthday: {record[3]}\nEmail: {record[4]}\nPassword: {record[5]}')
            else:
                print('No information found with the given ID.')
        except:
            break

def update_information_by_id():
    view_all_information()
    try:
        update_id = int(input('\nEnter the ID to update: ').strip())
        cursor_data.execute('SELECT * FROM information WHERE id = ?', (update_id,))
        record = cursor_data.fetchone()
        if not record:
            print('No records found for ID:', update_id)
            return
        
        print(f'\nCurrent information:\n  Name: {record[1]}\n  Location: {record[2]}\n  Birthday: {record[3]}\n  Email: {record[4]}\n  Password: {record[5]}')
        print('\n**Leave blank to keep current information**\n')
        new_information = [
            input('New Name: ').strip() or record[1],
            input('New Location: ').strip() or record[2],
            input('New Birthday (dd/mm/yyyy): ').strip() or record[3],
            input('New Email: ').strip() or record[4],
            input('New Password: ').strip() or record[5]
        ]
        
        if input(f'\nUpdate record with id {update_id}? (y/n): ').strip().lower() == 'y':
            cursor_data.execute('''
            UPDATE information
            SET name = ?, location = ?, birthday = ?, email = ?, password = ?
            WHERE id = ?''', (*new_information, update_id))
            data.commit()
    except:
        print("Invalid input! ID must be a number.")

def delete_information_by_id():
    view_all_information()
    print('\nDelete Information By ID')
    try:
        delete_id = int(input('\nEnter the ID to delete: ').strip())
        if input(f'Delete the record with ID {delete_id} (y/n): ').strip().lower() == 'y':
            cursor_data.execute('DELETE FROM information WHERE id = ?', (delete_id,))
    except:
        print("Invalid input! ID must be a number.")

def delete_all_information():
    if input('Delete all information? (y/n): ').strip().lower() == 'y':
        cursor_data.execute('DELETE FROM information')
        print('Delete all information successfull')

def main():
    """Main function to run the personal information generator."""
    options = {
        1: generate_single_information,
        2: generate_multiple_information,
        3: view_all_information,
        4: get_information_by_id,
        5: update_information_by_id,
        6: delete_information_by_id,
        7: delete_all_information
    }

    while True:
        try:
            clear_screen()
            print('''┌────────────────────────────────┐
▼ Personal Information Generator ▼
└────────────────────────────────┘\n''')
            for key, value in options.items():
                print(f'  [{key:02}] {value.__name__.replace("_", " ").title()}')
            print('  [00] Exit')
            option = int(input('\nChoose an option: '))
            if option in options:
                options[option]()
                input('\nPress any key to continue! ')
            elif option == 0:
                break
            else:
                print('Invalid option! Please try again.')
        except ValueError:
            print('Invalid option! Please enter a valid number.')
        except Exception as e:
            print('An error occurred:', str(e))

try:
    main()
finally:
    resources.close()
    data.close()