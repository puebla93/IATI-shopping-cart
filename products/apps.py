from django.apps import AppConfig
from django.core.management import call_command


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"

    def ready(self):
        # Load initial data
        call_command("loaddata", "initial_stock.yaml")
        # Add cron job
        call_command("crontab", "add")
