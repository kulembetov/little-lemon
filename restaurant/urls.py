from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, CartViewSet, OrderViewSet, ManagerGroupView, home, about, menu, menu_item_detail, book, assign_group, manager_dashboard, create_group

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/manager/assign-group/', ManagerGroupView.as_view(), name='assign-group'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('assign-group/', assign_group, name='assign_group'),
    path('manager-dashboard/', manager_dashboard, name='manager_dashboard'),
    path('create-group/', create_group, name='create_group'),
] 