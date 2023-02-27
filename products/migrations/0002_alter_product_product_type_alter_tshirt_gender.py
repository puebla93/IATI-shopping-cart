# Generated by Django 4.1.7 on 2023-02-26 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_type',
            field=models.CharField(choices=[('Cap', 'Cap'), ('Tshirt', 'Tshirt')], editable=False, max_length=20),
        ),
        migrations.AlterField(
            model_name='tshirt',
            name='gender',
            field=models.CharField(choices=[('Man', 'Man'), ('Woman', 'Woman'), ('Unisex', 'Unisex')], max_length=20),
        ),
    ]
