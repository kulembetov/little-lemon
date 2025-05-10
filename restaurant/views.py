from django.shortcuts import render, get_object_or_404
from .models import MenuItem
from .forms import BookingForm
from django.contrib import messages
import random

def home(request):
    items = list(MenuItem.objects.all())
    featured_items = random.sample(items, min(3, len(items))) if items else []
    return render(request, 'restaurant/home.html', {'featured_items': featured_items})

def about(request):
    return render(request, 'restaurant/about.html')

def menu(request):
    items = MenuItem.objects.all().order_by('name')
    return render(request, 'restaurant/menu.html', {'items': items})

def menu_item_detail(request, id):
    item = get_object_or_404(MenuItem, id=id)
    return render(request, 'restaurant/menu_item_detail.html', {'item': item})

def book(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your table has been booked!')
            form = BookingForm() 
    else:
        form = BookingForm()
    return render(request, 'restaurant/book.html', {'form': form})
