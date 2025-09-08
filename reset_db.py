import os
import shutil
import subprocess
from decouple import config

# Get database configuration from .env file
DB_NAME = config('DB_NAME', default='denew_db')
DB_USER = config('DB_USER', default='denew_user')

# Reset PostgreSQL database
try:
    # Drop database if it exists
    subprocess.run(['psql', '-U', DB_USER, '-c', f'DROP DATABASE IF EXISTS {DB_NAME};'], check=False)
    print(f'Existing database {DB_NAME} dropped if it existed.')
    
    # Create a new empty database
    subprocess.run(['psql', '-U', DB_USER, '-c', f'CREATE DATABASE {DB_NAME};'], check=True)
    print(f'New empty PostgreSQL database {DB_NAME} created.')
except Exception as e:
    print(f'Error with PostgreSQL operations: {e}')
    print('Make sure PostgreSQL is running and credentials are correct in .env file')

# Find and clean all migration files except __init__.py
app_dirs = ['accounts', 'core']
for app in app_dirs:
    migrations_dir = os.path.join('denew_backend', app, 'migrations')
    if os.path.exists(migrations_dir):
        print(f'Cleaning migrations in {migrations_dir}')
        for filename in os.listdir(migrations_dir):
            filepath = os.path.join(migrations_dir, filename)
            if os.path.isfile(filepath) and filename != '__init__.py' and filename.endswith('.py'):
                os.remove(filepath)
                print(f'  Removed {filename}')

# Create empty __init__.py files if they don't exist
for app in app_dirs:
    migrations_dir = os.path.join('denew_backend', app, 'migrations')
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
    init_file = os.path.join(migrations_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            pass
        print(f'Created {init_file}')

print('\nDatabase and migrations reset complete. Now run:')
print('python manage.py makemigrations')
print('python manage.py migrate')
