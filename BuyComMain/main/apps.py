from django.apps import AppConfig

def ready(self):
    import main.signals

class MainConfig(AppConfig):
    name = "main"
