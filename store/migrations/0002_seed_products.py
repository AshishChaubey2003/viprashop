from django.db import migrations


def seed_products(apps, schema_editor):
    """
    3 fixed products database mein daalo.
    Yeh migration ek baar chalti hai automatically.
    """
    Product = apps.get_model('store', 'Product')

    products = [
        {
            'name': 'VipraTech Mechanical Keyboard',
            'description': 'RGB backlit, tactile switches, build quality excellent',
            'price': 2999.00,
            'image_emoji': '⌨️',
        },
        {
            'name': 'VipraTech Wireless Mouse',
            'description': '2.4GHz wireless, ergonomic design, 12 months battery',
            'price': 1499.00,
            'image_emoji': '🖱️',
        },
        {
            'name': 'VipraTech USB-C Hub',
            'description': '7-in-1 hub: HDMI, USB 3.0 x3, SD card, PD charging',
            'price': 999.00,
            'image_emoji': '🔌',
        },
    ]

    for p in products:
        Product.objects.get_or_create(name=p['name'], defaults=p)


def unseed_products(apps, schema_editor):
    """Rollback ke liye - products delete karo"""
    Product = apps.get_model('store', 'Product')
    Product.objects.filter(name__startswith='VipraTech').delete()


class Migration(migrations.Migration):

    # Yeh migration 0001 ke baad chalegi
    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]