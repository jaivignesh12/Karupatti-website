import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karupatti.settings')
django.setup()

from products.models import Category, Product
from accounts.models import UserProfile

def seed():
    print("Seeding categories...")
    cats = {
        'solid': Category.objects.get_or_create(name='Solid Blocks', slug='solid-blocks', icon='bakery_dining', description='Traditional hand-pressed jaggery blocks')[0],
        'liquid': Category.objects.get_or_create(name='Liquid Nectar', slug='liquid-nectar', icon='water_drop', description='Slow-simmered liquid palm gold')[0],
        'blends': Category.objects.get_or_create(name='Artisanal Blends', slug='artisanal-blends', icon='auto_awesome', description='Infused with natural spices')[0],
        'rare': Category.objects.get_or_create(name='Rare Batch', slug='rare-batch', icon='eco', description='Limited edition from ancient groves')[0],
    }

    print("Seeding products...")
    products_data = [
        {
            'name': 'Karupatti Kadalai Mittai',
            'slug': 'karupatti-kadalai-mittai',
            'description': 'Traditional peanut candy made with roasted peanuts and pure palm jaggery. Crunchy, healthy, and packed with protein and iron. A guilt-free authentic snack. Net weight: 250g per pack.',
            'short_description': 'Crunchy peanut candy with pure palm jaggery – 250g pack.',
            'price': 150,
            'category': cats['solid'],
            'stock': 100,
            'badge': 'Best Seller',
            'badge_style': 'bg-primary/80 text-on-primary',
            'image_url': '/video/Karupatti-Kadalaimittai.png',
            'weight': '250g',
            'is_featured': True,
            'iron_content': '8.5mg',
            'gi_index': '40 Low',
        },
        {
            'name': 'Pure Karupatti Block',
            'slug': 'pure-karupatti-block-1',
            'description': 'Hand-pressed pure palm jaggery blocks. Rich in minerals and perfect as a healthy alternative to refined sugar in your daily tea or coffee. Slowly simmered for authentic taste. Net weight: 500g per block.',
            'short_description': 'Authentic hand-pressed palm jaggery blocks – 500g.',
            'price': 450,
            'category': cats['solid'],
            'stock': 150,
            'badge': 'Organic',
            'badge_style': 'bg-tertiary-container/80 text-on-tertiary-container',
            'image_url': '/video/karupatti1.jpg',
            'weight': '500g',
            'is_featured': True,
            'iron_content': '11.4mg',
            'gi_index': '35 Low',
        },
        {
            'name': 'Premium Karupatti Pieces',
            'slug': 'premium-karupatti-pieces',
            'description': 'Broken premium karupatti pieces for easy usage. Made from pure palm nectar, these pieces melt easily and provide a rich caramel flavor to any dish. Net weight: 500g per pack.',
            'short_description': 'Easy-to-use premium karupatti pieces – 500g pack.',
            'price': 460,
            'category': cats['solid'],
            'stock': 80,
            'badge': '',
            'badge_style': '',
            'image_url': '/video/karupatti2.webp',
            'weight': '500g',
            'is_featured': True,
            'iron_content': '10.5mg',
            'gi_index': '36 Low',
        },
        {
            'name': 'Karupatti Mysore Pak',
            'slug': 'karupatti-mysore-pak',
            'description': 'A healthy twist to the classic South Indian sweet. Made with pure ghee, gram flour, and sweetened entirely with natural palm jaggery for a rich, melt-in-mouth experience. Net weight: 500g box.',
            'short_description': 'Classic Mysore Pak with palm jaggery – 500g box.',
            'price': 650,
            'category': cats['blends'],
            'stock': 50,
            'badge': 'Premium',
            'badge_style': 'bg-surface-container-highest/80 text-on-surface',
            'image_url': '/video/karupatti-mysorepaak.webp',
            'weight': '500g',
            'is_featured': True,
            'iron_content': '5.2mg',
            'gi_index': '45 Medium',
        },
        {
            'name': 'Karupatti Kaju Katli',
            'slug': 'karupatti-kaju-katli',
            'description': 'Luxurious cashew fudge naturally sweetened with premium karupatti instead of sugar. A guilt-free indulgence that melts in your mouth and offers the rich taste of cashews and palm nectar. Net weight: 500g box.',
            'short_description': 'Cashew fudge sweetened with karupatti – 500g box.',
            'price': 950,
            'category': cats['blends'],
            'stock': 30,
            'badge': 'Rare',
            'badge_style': 'bg-surface-container-highest/80 text-on-surface',
            'image_url': '/video/karupatti-kaju-katli.png',
            'weight': '500g',
            'is_featured': True,
            'iron_content': '4.8mg',
            'gi_index': '42 Low',
        },
        {
            'name': 'Karupatti Powder',
            'slug': 'karupatti-powder',
            'description': 'Finely ground pure palm jaggery powder. Dissolves instantly in hot beverages and baking recipes, making it the perfect healthy sugar substitute for your daily needs. Net weight: 500g pack.',
            'short_description': 'Instant dissolving palm jaggery powder – 500g pack.',
            'price': 480,
            'category': cats['solid'],
            'stock': 120,
            'badge': '',
            'badge_style': '',
            'image_url': '/video/karupatti-powder.png',
            'weight': '500g',
            'is_featured': True,
            'iron_content': '11.0mg',
            'gi_index': '35 Low',
        },
        {
            'name': 'Karupatti Standard Block',
            'slug': 'karupatti-standard-block',
            'description': 'Our standard grade authentic palm jaggery blocks, crafted using traditional methods to retain maximum nutrients and natural sweetness. Net weight: 500g per block.',
            'short_description': 'Standard authentic palm jaggery blocks – 500g.',
            'price': 400,
            'category': cats['solid'],
            'stock': 200,
            'badge': '',
            'badge_style': '',
            'image_url': '/video/karupatti.webp',
            'weight': '500g',
            'is_featured': True,
            'iron_content': '10.8mg',
            'gi_index': '35 Low',
        }
    ]

    for p_data in products_data:
        Product.objects.get_or_create(slug=p_data['slug'], defaults=p_data)

    # Create admin user
    print("Creating admin user...")
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@karupattikadai.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    admin_user, created = UserProfile.objects.get_or_create(
        user_id='admin-user-001',
        defaults={
            'email': admin_email,
            'full_name': 'Admin',
            'is_admin': True,
        }
    )
    
    # Always update email and hash password to ensure it matches .env
    admin_user.email = admin_email
    import hashlib
    admin_user.password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    admin_user.save()



    print(f"Done! Seeded {Category.objects.count()} categories, {Product.objects.count()} products, {UserProfile.objects.count()} users")

if __name__ == '__main__':
    seed()
