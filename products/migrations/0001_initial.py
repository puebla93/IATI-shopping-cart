# Generated by Django 4.1.7 on 2023-02-24 16:56

from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_type', models.CharField(choices=[('C', 'Cap'), ('T', 'Tshirt')], max_length=1)),
                ('main_color', models.CharField(max_length=20)),
                ('secondary_colors', models.CharField(max_length=200)),
                ('brand', models.CharField(max_length=50)),
                ('inclusion_date', models.DateField()),
                ('photo_url', models.URLField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=4)),
                ('initial_stock', models.PositiveIntegerField(editable=False)),
                ('current_stock', models.PositiveIntegerField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cap',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.product')),
                ('logo_color', models.CharField(max_length=20)),
            ],
            bases=('products.product',),
        ),
        migrations.CreateModel(
            name='Tshirt',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='products.product')),
                ('size', models.CharField(max_length=20)),
                ('composition', models.JSONField(validators=[products.models.validate_tshirt_materials, products.models.validate_percentages_sum])),
                ('gender', models.CharField(choices=[('M', 'Man'), ('W', 'Woman'), ('U', 'Unisex')], max_length=1)),
                ('has_sleeves', models.BooleanField()),
            ],
            bases=('products.product',),
        ),
    ]
