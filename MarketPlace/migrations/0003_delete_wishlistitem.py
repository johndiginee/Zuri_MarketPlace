# Generated by Django 4.2.6 on 2023-10-10 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MarketPlace', '0002_productsubcategory_product_subcategory_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='WishListItem',
        ),
    ]
