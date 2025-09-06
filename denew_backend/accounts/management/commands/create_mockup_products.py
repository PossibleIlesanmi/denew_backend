from django.core.management.base import BaseCommand
from denew_backend.accounts.models import Product
import random

class Command(BaseCommand):
    help = 'Creates 40 mockup products for the task system'

    def handle(self, *args, **options):
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleared existing products'))

        # Product categories
        categories = ['Electronics', 'Fashion', 'Home', 'Beauty', 'Sports', 'Books', 'Toys', 'Food']
        
        # Product name templates
        name_templates = [
            '{} {}',  # Category + Item
            'Premium {} {}',  # Premium + Category + Item
            '{} {} Pro',  # Category + Item + Pro
            'Deluxe {} {}',  # Deluxe + Category + Item
            'Smart {} {}',  # Smart + Category + Item
        ]
        
        # Items per category
        electronics = ['Smartphone', 'Laptop', 'Headphones', 'Tablet', 'Camera', 'Speaker', 'Smartwatch', 'TV']
        fashion = ['Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes', 'Hat', 'Bag', 'Sunglasses']
        home = ['Sofa', 'Lamp', 'Table', 'Chair', 'Bed', 'Rug', 'Mirror', 'Clock']
        beauty = ['Perfume', 'Makeup', 'Skincare', 'Haircare', 'Nail Polish', 'Lotion', 'Serum', 'Mask']
        sports = ['Sneakers', 'Ball', 'Racket', 'Weights', 'Yoga Mat', 'Bike', 'Helmet', 'Gloves']
        books = ['Novel', 'Cookbook', 'Biography', 'Self-Help', 'History', 'Science', 'Fiction', 'Poetry']
        toys = ['Doll', 'Action Figure', 'Board Game', 'Puzzle', 'Plush', 'Building Blocks', 'Remote Car', 'Drone']
        food = ['Coffee', 'Tea', 'Chocolate', 'Snacks', 'Pasta', 'Sauce', 'Spices', 'Cookies']
        
        category_items = {
            'Electronics': electronics,
            'Fashion': fashion,
            'Home': home,
            'Beauty': beauty,
            'Sports': sports,
            'Books': books,
            'Toys': toys,
            'Food': food
        }
        
        # Icons (using simple text representations)
        icons = ['📱', '💻', '👕', '🏠', '💄', '🏀', '📚', '🧸', '🍔', '⌚', '👟', '🛋️', '🎮', '🎧', '👜', '🖼️', '🍵']
        
        # Create 40 products
        products_created = 0
        used_names = set()
        
        while products_created < 40:
            category = random.choice(categories)
            item = random.choice(category_items[category])
            name_template = random.choice(name_templates)
            name = name_template.format(category, item)
            
            # Ensure unique names
            if name in used_names:
                continue
            
            used_names.add(name)
            
            # Generate price between $10 and $1000
            price = round(random.uniform(10, 1000), 2)
            
            # Randomly decide if it's a combined product (20% chance)
            is_combined = random.random() < 0.2
            
            # Select a random icon
            icon = random.choice(icons)
            
            # Create the product
            Product.objects.create(
                name=name,
                icon=icon,
                price=price,
                is_combined=is_combined
            )
            
            products_created += 1
            self.stdout.write(f'Created product {products_created}/40: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {products_created} mockup products'))