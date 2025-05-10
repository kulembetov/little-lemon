from restaurant.models import MenuItem

def clean_menu():
    MenuItem.objects.all().delete()
    print('All menu items have been deleted.') 