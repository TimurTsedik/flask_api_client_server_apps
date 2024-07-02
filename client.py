import requests

BASE_URL = 'http://127.0.0.1:5000'

def register(email, password):
    response = requests.post(f'{BASE_URL}/register', json={'email': email, 'password': password})
    return response.json()

def login(email, password):
    session = requests.Session()
    response = session.post(f'{BASE_URL}/login', json={'email': email, 'password': password})
    if response.status_code == 200:
        return session, response.json()
    else:
        return None, response.json()

def create_ad(session, title, description):
    response = session.post(f'{BASE_URL}/ads', json={'title': title, 'description': description})
    return response.json()

def get_ad(ad_id):
    response = requests.get(f'{BASE_URL}/ads/{ad_id}')
    return response.json()

def update_ad(session, ad_id, title=None, description=None):
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    response = session.put(f'{BASE_URL}/ads/{ad_id}', json=data)
    return response.json()

def delete_ad(session, ad_id):
    response = session.delete(f'{BASE_URL}/ads/{ad_id}')
    return response.json()

def logout(session):
    response = session.post(f'{BASE_URL}/logout')
    return response.json()

if __name__ == '__main__':
    # Register a new user
    print("Registering a new user...")
    print(register('user@example.com', 'password'))

    # Login the user
    print("Logging in the user...")
    session, login_response = login('user@example.com', 'password')
    print(login_response)

    if session:
        # Create a new ad
        print("Creating a new ad...")
        print(create_ad(session, 'My First Ad', 'This is a description of my first ad'))

        # Get the ad
        print("Getting the ad...")
        print(get_ad(1))

        # Update the ad
        print("Updating the ad...")
        print(update_ad(session, 1, title='Updated Ad', description='Updated description'))

        # Delete the ad
        print("Deleting the ad...")
        print(delete_ad(session, 1))

        # Logout the user
        print("Logging out the user...")
        print(logout(session))
