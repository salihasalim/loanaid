from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('loan-data/', views.get_loan_data, name='get_loan_data'),
    path('loan-totals/', views.get_loan_totals, name='get_loan_totals'),
]
