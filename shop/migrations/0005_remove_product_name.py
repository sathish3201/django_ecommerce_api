# Generated by Django 5.0.6 on 2025-02-26 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_product_brand_product_category_product_deleted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='name',
        ),
    ]
