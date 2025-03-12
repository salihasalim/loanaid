from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.template.context_processors import request

from UserApp.models import *
from UserApp.forms import *


from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist


def dashboard(request):
    # Retrieve the correct session data
    user_id = request.session.get('user_id')  # Match the key from login session
    user_type = request.session.get('user_type')

    if user_id is None or user_type != 'staff':  
        print("Unauthorized access attempt, redirecting to login.")  
        return redirect('/login')  

    try:
        user = StaffModel.objects.get(pk=user_id)  # Use `pk` (not `staff_id` unless that's your primary key)
    except StaffModel.DoesNotExist:
        print(f"Staff with ID {user_id} does not exist.")  
        return redirect('/login')

    # Fetch all loans and franchises (only accessible by staff)
    all_loans = LoanApplicationModel.objects.all()
    all_franchises = Franchise.objects.all()

    context = {
        'user': user,
        'username': f"{user.first_name} {user.last_name}" if user.last_name else user.first_name,
        'all_loans': all_loans,
        'all_franchises': all_franchises,
    }

    return render(request, 'dashboard.html', context)



def get_loan_data(request):
    loan_data = LoanApplicationModel.objects.annotate(month=TruncMonth('followup_date')) \
        .values('month') \
        .annotate(loan_count=Count('form_id')) \
        .order_by('month')
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    loan_counts = [0] * 12

    for data in loan_data:
        loan_counts[data['month'].month - 1] = data['loan_count']

    return JsonResponse({'months': months, 'loan_counts': loan_counts})



def get_loan_totals(request):
    loan_data = LoanApplicationModel.objects.annotate(month=TruncMonth('followup_date')) \
        .values('month') \
        .annotate(total_loans=Count('form_id')) \
        .order_by('month')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    total_loans = [0] * 12  # Initialize with 0s

    for data in loan_data:
        total_loans[data['month'].month - 1] = data['total_loans']

    response_data = {
        'months': months,
        'total_loans': total_loans,
    }

    return JsonResponse(response_data)