from django.urls import path
from UserApp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.home, name='dashboard'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('view_profile/<int:staff_id>', views.view_staffs, name = 'view_profile'),
    path('create-user/', views.create_staff, name='create_staff'),
    path('list_staff/',views.list_staff,name='list_staff'),
    path('delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('delete-file/<int:id>/', views.delete_files, name='delete_file'),
]
   