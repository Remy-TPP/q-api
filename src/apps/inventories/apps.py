from django.apps import AppConfig


class InventoriesConfig(AppConfig):
    name = 'apps.inventories'

    def ready(self):
        import apps.inventories.signals
