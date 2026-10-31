from django.core.management.base import BaseCommand
from shop.models import Category, Product

DATA = {
    "Phones": [("Galaxy A15 128GB", 18500, "Bright AMOLED display and a 5000mAh battery."),
               ("Tecno Spark 20", 14200, "Fast charging, 50MP camera."),
               ("Infinix Hot 40", 15800, "Smooth 120Hz screen for gaming.")],
    "Electronics": [("Bluetooth Speaker", 3200, "Portable, waterproof, 12-hour battery."),
                    ("Wireless Earbuds", 2500, "Noise isolation with charging case."),
                    ("32-inch Smart TV", 21000, "HD, built-in streaming apps.")],
    "Fashion": [("Running Sneakers", 4500, "Lightweight and breathable."),
                ("Denim Jacket", 3800, "Classic fit, durable denim.")],
    "Home": [("Electric Kettle 1.8L", 1900, "Auto shut-off, stainless steel."),
             ("Non-stick Cookware Set", 6500, "7-piece set, induction ready.")],
}


class Command(BaseCommand):
    help = "Load demo categories and products"

    def handle(self, *args, **opts):
        from django.utils.text import slugify
        for cat, items in DATA.items():
            c, _ = Category.objects.get_or_create(name=cat, defaults={"slug": slugify(cat)})
            for name, price, desc in items:
                slug = slugify(name)
                Product.objects.get_or_create(slug=slug, defaults=dict(
                    category=c, name=name, price=price, description=desc, stock=25,
                    image_url=f"https://picsum.photos/seed/{slug}/400/300"))
        self.stdout.write(self.style.SUCCESS("Demo data loaded."))
