# Generated by Django 5.0.6 on 2025-02-26 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_product_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='title',
            field=models.CharField(default='title', max_length=50),
        ),
    ]
