from django.shortcuts import render, get_object_or_404
from .models import MenuItem
from .forms import BookingForm
from django.contrib import messages
import random
from rest_framework import viewsets, status, generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from .models import Category, Cart, Order, OrderItem
from .serializers import (
    UserSerializer, GroupSerializer, CategorySerializer, MenuItemSerializer,
    CartSerializer, OrderSerializer, OrderItemSerializer
)
from .permissions import IsAdmin, IsManager, IsDeliveryCrew, IsCustomer
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden

def home(request):
    items = list(MenuItem.objects.all())
    featured_items = random.sample(items, min(3, len(items))) if items else []
    item_of_the_day = MenuItem.objects.filter(is_item_of_the_day=True).first()
    return render(request, 'restaurant/home.html', {'featured_items': featured_items, 'item_of_the_day': item_of_the_day})

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

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'set_item_of_the_day']:
            return [IsAdmin() or IsManager()]
        return [AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def set_item_of_the_day(self, request, pk=None):
        MenuItem.objects.filter(is_item_of_the_day=True).update(is_item_of_the_day=False)
        item = self.get_object()
        item.is_item_of_the_day = True
        item.save()
        return Response({'status': 'item of the day set', 'item': item.name})

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        unit_price = menuitem.price
        price = unit_price * quantity
        serializer.save(user=self.request.user, unit_price=unit_price, price=price)

    def perform_update(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        unit_price = menuitem.price
        price = unit_price * quantity
        serializer.save(unit_price=unit_price, price=price)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise serializers.ValidationError('Cart is empty')
        total = cart_items.aggregate(total=Sum('price'))['total'] or 0
        order = serializer.save(user=user, total=total)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        cart_items.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def assign_delivery_crew(self, request, pk=None):
        order = self.get_object()
        crew_id = request.data.get('crew_id')
        crew = get_object_or_404(User, id=crew_id)
        order.delivery_crew = crew
        order.status = 'in_progress'
        order.save()
        return Response({'status': 'assigned', 'crew': crew.username})

    @action(detail=True, methods=['post'], permission_classes=[IsDeliveryCrew])
    def mark_delivered(self, request, pk=None):
        order = self.get_object()
        order.status = 'delivered'
        order.save()
        return Response({'status': 'delivered'})

class ManagerGroupView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin|IsManager]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        group_name = request.data.get('group')
        user = get_object_or_404(User, id=user_id)
        group = get_object_or_404(Group, name=group_name)
        user.groups.add(group)
        return Response({'status': 'added', 'user': user.username, 'group': group.name})

def assign_group(request):
    if not request.user.is_authenticated or not (request.user.is_superuser or request.user.groups.filter(name='manager').exists()):
        return HttpResponseForbidden('You do not have permission to access this page.')
    users = User.objects.all()
    groups = Group.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        if user_id and group_id:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            user.groups.add(group)
            messages.success(request, f"Added {user.username} to {group.name}.")
    return render(request, 'restaurant/assign_group.html', {'users': users, 'groups': groups})

@login_required
def manager_dashboard(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='manager').exists()):
        return HttpResponseForbidden('You do not have permission to access this page.')
    return render(request, 'restaurant/manager_dashboard.html')

def create_group(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden('You do not have permission to access this page.')
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                messages.success(request, f"Group '{group_name}' created.")
            else:
                messages.info(request, f"Group '{group_name}' already exists.")
    return render(request, 'restaurant/create_group.html')
