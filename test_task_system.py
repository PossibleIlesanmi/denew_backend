import requests
import json
import time

# Base URL for API
BASE_URL = 'http://127.0.0.1:8000/api'

# Test user credentials
USERNAME = 'testuser2'
PASSWORD = 'testpass123'
EMAIL = 'testuser2@example.com'
WITHDRAWAL_PIN = '1234'

def print_separator():
    print('\n' + '-'*50 + '\n')

# Helper function to safely print response
def safe_print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        json_response = response.json()
        print(f"Response: {json.dumps(json_response, indent=2)}")
        return json_response
    except json.JSONDecodeError:
        print(f"Response: {response.text}")
        return None

# 1. Register a new user
def register_user():
    print("1. Registering a new user...")
    url = f"{BASE_URL}/register/"
    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'email': EMAIL,
        'full_name': 'Test User',
        'phone_number': '1234567890',
        'withdrawal_password': WITHDRAWAL_PIN
    }
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        json_response = safe_print_response(response)
        
        if response.status_code == 201 and json_response:
            return json_response.get('tokens', {}).get('access')
        return None
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

# 2. Login with existing user
def login_user():
    print("2. Logging in...")
    url = f"{BASE_URL}/login/"
    data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        json_response = safe_print_response(response)
        
        if response.status_code == 200 and json_response:
            return json_response.get('tokens', {}).get('access')
        return None
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

# 3. Get user profile
def get_profile(token):
    print("3. Getting user profile...")
    url = f"{BASE_URL}/profile/"
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        safe_print_response(response)
    except requests.RequestException as e:
        print(f"Error: {e}")

# 4. Start a task set
def start_task_set(token):
    print("4. Starting a task set...")
    url = f"{BASE_URL}/tasks/start-set/"
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(url, headers=headers)
        safe_print_response(response)
    except requests.RequestException as e:
        print(f"Error: {e}")

# 5. Get current task
def get_current_task(token):
    print("5. Getting current task...")
    url = f"{BASE_URL}/tasks/current/"
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        json_response = safe_print_response(response)
        
        if response.status_code == 200 and json_response and json_response.get('task'):
            return json_response['task']['id']
        return None
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

# 6. Start a specific task
def start_task(token, task_id):
    print(f"6. Starting task {task_id}...")
    url = f"{BASE_URL}/tasks/start/"
    headers = {'Authorization': f'Bearer {token}'}
    data = {'task_id': task_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        safe_print_response(response)
    except requests.RequestException as e:
        print(f"Error: {e}")

# 7. Submit a task
def submit_task(token, task_id):
    print(f"7. Submitting task {task_id}...")
    url = f"{BASE_URL}/tasks/complete/"
    headers = {'Authorization': f'Bearer {token}'}
    data = {'task_id': task_id}
    try:
        response = requests.post(url, json=data, headers=headers)
        safe_print_response(response)
    except requests.RequestException as e:
        print(f"Error: {e}")

# 8. List all tasks
def list_tasks(token):
    print("8. Listing all tasks...")
    url = f"{BASE_URL}/tasks/"
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        safe_print_response(response)
    except requests.RequestException as e:
        print(f"Error: {e}")

# 9. Get dashboard data
def get_dashboard(token):
    print("9. Getting dashboard data...")
    url = f"{BASE_URL}/dashboard/"
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        safe_print_response(response)
    except requests.RequestException as e:
        print(f"Error: {e}")

# Main test flow
def main():
    # Try to login first, if fails, register
    token = login_user()
    if not token:
        print_separator()
        print("Login failed, trying to register...")
        token = register_user()
    
    if not token:
        print("Failed to authenticate. Exiting.")
        return
    
    print_separator()
    get_profile(token)
    
    print_separator()
    get_dashboard(token)
    
    print_separator()
    start_task_set(token)
    
    print_separator()
    task_id = get_current_task(token)
    
    if task_id:
        print_separator()
        start_task(token, task_id)
        
        print_separator()
        submit_task(token, task_id)
        
        print_separator()
        # Get the next task that was created
        task_id = get_current_task(token)
        
        if task_id:
            print("\nSuccessfully got next task! Task system is working as expected.")
        else:
            print("\nFailed to get next task. Task system may not be working correctly.")
    else:
        print("\nFailed to get current task. Task system may not be working correctly.")
    
    print_separator()
    list_tasks(token)

if __name__ == "__main__":
    main()