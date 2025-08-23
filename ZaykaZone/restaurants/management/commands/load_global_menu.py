from django.core.management.base import BaseCommand
from restaurants.models import MenuCategory, MenuItem

class Command(BaseCommand):
    help = 'Load predefined global menu categories and items'

    def handle(self, *args, **kwargs):
        menu_data = {
            "Chef's Signature": [
                ("Smoky Veg Bisque", 420),
                ("TMC Signature Broccoli Cheddar", 462)
            ],
            "Shuruvat": [
                ("Paneer Tikka", 310),
                ("Hara Bhara Kebab", 290)
            ],
            "Dil Hindustani": [
                ("Dal Makhani", 270),
                ("Paneer Butter Masala", 320)
            ],
            "Chaat": [
                ("Papdi Chaat", 160),
                ("Dahi Puri", 150),
                ("Raj Kachori", 180)
            ],
            "Soup": [
                ("Tomato Soup", 140),
                ("Sweet Corn Soup", 150)
            ],
            "Pesh": [
                ("Stuffed Mushroom", 290),
                ("Paneer Peshawari", 340)
            ],
            "Angaron": [
                ("Tandoori Paneer Tikka", 330),
                ("Malai Soya Chaap", 310)
            ],
            "Baked": [
                ("Baked Macaroni", 280),
                ("Baked Lasagna", 300)
            ]
        }

        for cat_name, items in menu_data.items():
            category, created = MenuCategory.objects.get_or_create(name=cat_name, is_global=True)
            for item_name, price in items:
                MenuItem.objects.get_or_create(
                    name=item_name,
                    price=price,
                    category=category,
                    restaurant=None
                )

        self.stdout.write(self.style.SUCCESS('✔ Global menu items inserted successfully.'))
