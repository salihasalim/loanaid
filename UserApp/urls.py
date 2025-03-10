from django.urls import path
from UserApp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('view_profile/<int:id>', views.view_staffs, name = 'view_profile'),
    path('create-user/', views.create_staff, name='create_staff'),

    path('delete-file/<int:id>/', views.delete_files, name='delete_file'),
]
