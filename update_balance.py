import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'denew_backend.settings')
django.setup()

# Import the User model
from denew_backend.accounts.models import User

# Update the balance for testuser2
try:
    user = User.objects.get(username='testuser2')
    user.balance = 150.00
    user.save()
    print(f"Updated balance for {user.username} to {user.balance}")
except User.DoesNotExist:
    print("User 'testuser2' not found")

# List all users and their balances
users = User.objects.all()
print("\nAll users and their balances:")
for user in users:
    print(f"{user.username}: {user.balance}")