import os
import shutil
import subprocess

# Reset PostgreSQL database
try:
    # Drop database if it exists
    subprocess.run(['psql', '-U', 'denew_user', '-c', 'DROP DATABASE IF EXISTS denew_db;'], check=False)
    print('Existing database dropped if it existed.')
    
    # Create a new empty database
    subprocess.run(['psql', '-U', 'denew_user', '-c', 'CREATE DATABASE denew_db;'], check=True)
    print('New empty PostgreSQL database created.')
except Exception as e:
    print(f'Error with PostgreSQL operations: {e}')
    print('Make sure PostgreSQL is running and credentials are correct in settings.py')

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

print('\nIf you still have migration issues, try:')
print('1. python manage.py migrate --fake accounts zero')
print('2. python manage.py migrate --fake admin zero')
print('3. python manage.py migrate --fake auth zero')
print('4. python manage.py migrate --fake contenttypes zero')
print('5. python manage.py migrate --fake sessions zero')
print('6. python manage.py migrate')