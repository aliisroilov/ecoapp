import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoapp.settings')
django.setup()

from django.contrib.auth.models import User
from eco.models import EcoTask, MerchItem, UserProfile
from datetime import datetime, timedelta

print("🌱 Seeding EcoApp database...")

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@ecoapp.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print(f"✓ Created superuser: admin / admin123")

# Create sample users
sample_users = [
    {'username': 'john_eco', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Green'},
    {'username': 'sarah_planet', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Earth'},
    {'username': 'mike_nature', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Forest'},
]

for user_data in sample_users:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password='password123',
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        # Update profile with some coins
        user.profile.coin_balance = 50
        user.profile.location = "New York, USA"
        user.profile.age = 25
        user.profile.bio = f"Eco enthusiast making the world greener!"
        user.profile.save()
        print(f"✓ Created user: {user_data['username']} / password123")

# Create sample eco tasks
eco_tasks = [
    {
        'title': 'Plant a Tree',
        'description': 'Plant a tree in your community and take a photo with it. Every tree helps reduce CO2 and provides oxygen for our planet!',
        'coin_reward': 50,
        'deadline': datetime.now() + timedelta(days=30)
    },
    {
        'title': 'Beach Cleanup',
        'description': 'Organize or participate in a beach cleanup. Collect at least 5kg of trash and document your efforts with photos.',
        'coin_reward': 75,
        'deadline': datetime.now() + timedelta(days=45)
    },
    {
        'title': 'Reduce Plastic Use',
        'description': 'Go plastic-free for one week. Use reusable bags, bottles, and containers. Share your journey and tips!',
        'coin_reward': 40,
        'deadline': datetime.now() + timedelta(days=60)
    },
    {
        'title': 'Start Composting',
        'description': 'Set up a composting system at home. Document the setup and show us your first batch of compost!',
        'coin_reward': 60,
        'deadline': datetime.now() + timedelta(days=90)
    },
    {
        'title': 'Public Transport Challenge',
        'description': 'Use only public transportation, bike, or walk for one month. Track your carbon savings!',
        'coin_reward': 80,
        'deadline': datetime.now() + timedelta(days=120)
    },
    {
        'title': 'Community Garden',
        'description': 'Create or join a community garden. Plant vegetables and share the harvest with your neighbors.',
        'coin_reward': 70,
        'deadline': datetime.now() + timedelta(days=60)
    },
    {
        'title': 'Zero Waste Shopping',
        'description': 'Shop at zero-waste stores or bulk sections. Use your own containers and avoid all packaging.',
        'coin_reward': 45,
        'deadline': datetime.now() + timedelta(days=30)
    },
    {
        'title': 'Energy Audit',
        'description': 'Conduct a home energy audit. Identify ways to reduce energy consumption and implement at least 3 changes.',
        'coin_reward': 55,
        'deadline': datetime.now() + timedelta(days=45)
    },
]

for task_data in eco_tasks:
    if not EcoTask.objects.filter(title=task_data['title']).exists():
        EcoTask.objects.create(**task_data)
        print(f"✓ Created task: {task_data['title']}")

# Create sample merchandise
merch_items = [
    {
        'name': 'Eco-Friendly Water Bottle',
        'description': 'Stainless steel, BPA-free water bottle that keeps drinks cold for 24 hours. Reduce plastic waste with this stylish bottle!',
        'coin_cost': 100,
        'stock_quantity': 50,
        'available': True
    },
    {
        'name': 'Reusable Bamboo Cutlery Set',
        'description': 'Travel cutlery set made from sustainable bamboo. Includes fork, knife, spoon, and chopsticks with carrying case.',
        'coin_cost': 75,
        'stock_quantity': 75,
        'available': True
    },
    {
        'name': 'Organic Cotton Tote Bag',
        'description': '100% organic cotton tote bag. Perfect for grocery shopping and everyday use. Say no to plastic bags!',
        'coin_cost': 50,
        'stock_quantity': 100,
        'available': True
    },
    {
        'name': 'Solar-Powered Phone Charger',
        'description': 'Portable solar charger for your devices. Harness the power of the sun wherever you go!',
        'coin_cost': 200,
        'stock_quantity': 25,
        'available': True
    },
    {
        'name': 'Beeswax Food Wraps Set',
        'description': 'Set of 5 reusable beeswax wraps to replace plastic wrap. Keep food fresh naturally!',
        'coin_cost': 60,
        'stock_quantity': 60,
        'available': True
    },
    {
        'name': 'Stainless Steel Straws Pack',
        'description': 'Set of 4 reusable metal straws with cleaning brush. Eliminate single-use plastic straws!',
        'coin_cost': 40,
        'stock_quantity': 100,
        'available': True
    },
    {
        'name': 'Eco T-Shirt',
        'description': 'Premium organic cotton t-shirt with eco-friendly print. Comfortable and sustainable!',
        'coin_cost': 120,
        'stock_quantity': 40,
        'available': True
    },
    {
        'name': 'Plant Growing Kit',
        'description': 'Complete kit to grow your own herbs at home. Includes seeds, pots, and organic soil.',
        'coin_cost': 90,
        'stock_quantity': 35,
        'available': True
    },
]

# Note: In production, you would need actual image files for merchandise
for item_data in merch_items:
    if not MerchItem.objects.filter(name=item_data['name']).exists():
        # Create without image for now
        MerchItem.objects.create(
            name=item_data['name'],
            description=item_data['description'],
            coin_cost=item_data['coin_cost'],
            stock_quantity=item_data['stock_quantity'],
            available=item_data['available'],
            image='merchandise/placeholder.jpg'  # You'll need to add actual images
        )
        print(f"✓ Created merchandise: {item_data['name']}")

print("\n🎉 Database seeded successfully!")
print("\n📝 Login credentials:")
print("   Superuser: admin / admin123")
print("   Sample user: john_eco / password123")
print("   Sample user: sarah_planet / password123")
print("   Sample user: mike_nature / password123")