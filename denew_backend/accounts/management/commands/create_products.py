from django.core.management.base import BaseCommand
from denew_backend.accounts.models import Product

class Command(BaseCommand):
    help = 'Create 48 products with icons for the task system'

    def handle(self, *args, **options):
        self.stdout.write('Creating products...')
        
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write('Cleared existing products')
        
        products = [
            # Electronics (10 products)
            {'name': 'Smart TV 55"', 'icon': 'https://cdn-icons-png.flaticon.com/512/545/545245.png', 'price': 599.99},
            {'name': 'Laptop Gaming', 'icon': 'https://cdn-icons-png.flaticon.com/512/3474/3474360.png', 'price': 1299.99},
            {'name': 'iPhone 15 Pro', 'icon': 'https://cdn-icons-png.flaticon.com/512/15047/15047435.png', 'price': 1099.99},
            {'name': 'Wireless Headphones', 'icon': 'https://cdn-icons-png.flaticon.com/512/3845/3845876.png', 'price': 249.99},
            {'name': 'Gaming Console', 'icon': 'https://cdn-icons-png.flaticon.com/512/686/686589.png', 'price': 499.99},
            {'name': 'Tablet Pro', 'icon': 'https://cdn-icons-png.flaticon.com/512/4948/4948689.png', 'price': 899.99},
            {'name': 'Smart Watch', 'icon': 'https://cdn-icons-png.flaticon.com/512/4392/4392454.png', 'price': 399.99},
            {'name': 'Bluetooth Speaker', 'icon': 'https://cdn-icons-png.flaticon.com/512/2058/2058175.png', 'price': 129.99},
            {'name': 'Camera DSLR', 'icon': 'https://cdn-icons-png.flaticon.com/512/685/685655.png', 'price': 799.99},
            {'name': 'Air Purifier', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933245.png', 'price': 299.99},

            # Home & Furniture (12 products)
            {'name': 'Dining Table', 'icon': 'https://cdn-icons-png.flaticon.com/512/1670/1670074.png', 'price': 449.99},
            {'name': 'Office Chair', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991148.png', 'price': 199.99},
            {'name': 'Sofa 3-Seater', 'icon': 'https://cdn-icons-png.flaticon.com/512/1670/1670071.png', 'price': 799.99},
            {'name': 'Bed Queen Size', 'icon': 'https://cdn-icons-png.flaticon.com/512/1670/1670076.png', 'price': 599.99},
            {'name': 'Wardrobe', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991159.png', 'price': 699.99},
            {'name': 'Coffee Table', 'icon': 'https://cdn-icons-png.flaticon.com/512/1670/1670073.png', 'price': 249.99},
            {'name': 'Bookshelf', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991161.png', 'price': 179.99},
            {'name': 'Desk Lamp', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991154.png', 'price': 89.99},
            {'name': 'Mirror Wall', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991153.png', 'price': 129.99},
            {'name': 'Plant Pot Large', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933286.png', 'price': 59.99},
            {'name': 'Curtains Set', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991156.png', 'price': 79.99},
            {'name': 'Carpet Persian', 'icon': 'https://cdn-icons-png.flaticon.com/512/2991/2991152.png', 'price': 299.99},

            # Kitchen & Appliances (10 products)
            {'name': 'Refrigerator', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933259.png', 'price': 899.99},
            {'name': 'Microwave Oven', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933256.png', 'price': 199.99},
            {'name': 'Coffee Maker', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933272.png', 'price': 149.99},
            {'name': 'Blender', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933274.png', 'price': 79.99},
            {'name': 'Toaster', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933257.png', 'price': 69.99},
            {'name': 'Air Fryer', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933270.png', 'price': 159.99},
            {'name': 'Washing Machine', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933258.png', 'price': 699.99},
            {'name': 'Dishwasher', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933260.png', 'price': 549.99},
            {'name': 'Electric Kettle', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933273.png', 'price': 39.99},
            {'name': 'Food Processor', 'icon': 'https://cdn-icons-png.flaticon.com/512/2933/2933275.png', 'price': 119.99},

            # Fashion & Accessories (8 products)
            {'name': 'Luxury Handbag', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553642.png', 'price': 299.99},
            {'name': 'Designer Shoes', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553651.png', 'price': 199.99},
            {'name': 'Leather Jacket', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553646.png', 'price': 249.99},
            {'name': 'Gold Watch', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553645.png', 'price': 899.99},
            {'name': 'Sunglasses', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553648.png', 'price': 149.99},
            {'name': 'Designer Belt', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553647.png', 'price': 89.99},
            {'name': 'Luxury Perfume', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553654.png', 'price': 129.99},
            {'name': 'Silk Scarf', 'icon': 'https://cdn-icons-png.flaticon.com/512/2553/2553649.png', 'price': 79.99},

            # Sports & Fitness (8 products)
            {'name': 'Treadmill Pro', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936719.png', 'price': 899.99},
            {'name': 'Dumbbell Set', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936699.png', 'price': 199.99},
            {'name': 'Yoga Mat Premium', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936696.png', 'price': 39.99},
            {'name': 'Mountain Bike', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936758.png', 'price': 799.99},
            {'name': 'Tennis Racket Pro', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936736.png', 'price': 149.99},
            {'name': 'Basketball Official', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936732.png', 'price': 29.99},
            {'name': 'Golf Club Set', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936734.png', 'price': 599.99},
            {'name': 'Running Shoes', 'icon': 'https://cdn-icons-png.flaticon.com/512/2936/2936697.png', 'price': 119.99},
        ]

        created_count = 0
        for product_data in products:
            product = Product.objects.create(**product_data)
            created_count += 1
            if created_count <= 5:  # Show first 5 as examples
                self.stdout.write(f'✅ Created: {product.name} - ${product.price}')
            
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Successfully created {created_count} products!')
        )
        
        # Show summary by category
        self.stdout.write('')
        self.stdout.write('📊 Products by Category:')
        self.stdout.write(f'📱 Electronics: 10 products')
        self.stdout.write(f'🏠 Home & Furniture: 12 products') 
        self.stdout.write(f'🍳 Kitchen & Appliances: 10 products')
        self.stdout.write(f'👕 Fashion & Accessories: 8 products')
        self.stdout.write(f'🏃 Sports & Fitness: 8 products')
        self.stdout.write('')
        self.stdout.write('✅ Your task system now has product icons!')