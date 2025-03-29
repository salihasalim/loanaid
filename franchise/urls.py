from django.urls import path
from . import views

urlpatterns = [
    # Admin can add franchises
    path('staff_upload/', views.staff_uploaded, name='staff_upload'),

    # View all staff assignments
    path('staff_assignments/', views.all_assignments, name='staff_assignments'),

    # Update a specific staff assignment
    path('edit/<uuid:franchise_id>/', views.edit_franchise, name='edit_franchise'),
    path("franchise/profile/", views.view_franchise_profile, name="view_franchise_profile"),


    # Franchise management
    path('franchise_dashboard/', views.franchise_dashboard, name='franchise_dashboard'),
    path('delete/<uuid:franchise_id>/', views.delete_franchise, name='delete_franchise'),
    path('add_franchise/', views.add_franchise, name='add_franchise'),
    path('list_franchise/', views.list_franchise, name='list_franchise'),
    path('franchise_logout/', views.franchise_logout, name='franchise_logout'),
]
