import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import Product, Category
print("Current models:")
print(f"Product fields: {[f.name for f in Product._meta.get_fields()]}")
print(f"Category count: {Category.objects.count()}")
