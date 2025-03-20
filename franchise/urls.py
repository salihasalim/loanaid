from django.urls import path
from . import views

urlpatterns = [
    # Admin can add franchises
    path('staff_upload/', views.staff_uploaded, name='staff_upload'),

    # View all staff assignments
    path('staff_assignments/', views.all_assignments, name='staff_assignments'),

    # Update a specific staff assignment
    path('update/<int:assignment_id>/', views.update_assignment, name='update_assignment'),

    # Franchise management
    path('franchise_dashboard/', views.franchise_dashboard, name='franchise_dashboard'),
    path('franchise_edit/', views.franchise_edit, name='franchise_edit'),
    path('franchise_logout/', views.franchise_logout, name='franchise_logout'),
    path('add_franchise/', views.add_franchise, name='add_franchise'),
    path('list_franchise/', views.list_franchise, name='list_franchise'),
]
