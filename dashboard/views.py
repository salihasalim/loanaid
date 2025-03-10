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
    # Debug: Check session data
    print(f"User session: {request.session.get('user', None)}")  # Debug statement
    
    user_id = request.session.get('user', None)
    user_type = request.session.get('user_type', None)

    if user_id is None:
        print("No user session found, redirecting to login.")  # Debug statement
        return redirect('/login')

    user = None

    # Fetch user based on the session data
    if user_type == 'admin':
        try:
            user = AdminModel.objects.get(admin_id=user_id)
        except AdminModel.DoesNotExist:
            print(f"Admin with ID {user_id} does not exist.")  # Debug statement
            return redirect('/login')

    elif user_type == 'franchise':
        try:
            user = Franchise.objects.get(franchise_id=user_id)
        except Franchise.DoesNotExist:
            print(f"Franchise with ID {user_id} does not exist.")  # Debug statement
            return redirect('/login')

    elif user_type == 'staff':
        try:
            user = StaffModel.objects.get(staff_id=user_id)
        except StaffModel.DoesNotExist:
            print(f"Staff with ID {user_id} does not exist.")  # Debug statement
            return redirect('/login')

    else:
        print("Unknown user type.")  # Debug statement
        return redirect('/login')

    # Fetch additional data like loan application, status, and progress
    if user_type == 'admin':
        username = f"{user.admin_first_name} {user.admin_last_name}" if user.admin_last_name else user.admin_first_name
        phoneno = user.admin_phone
    elif user_type == 'franchise':
        username = user.franchise_name
        phoneno = user.mobile_no
    elif user_type == 'staff':
        username = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        phoneno = user.phone_no

    try:
        loan_application = LoanApplicationModel.objects.get(phone_no=phoneno)
        status = loan_application.status_name.status_name if loan_application.status_name else "Application Started"
    except ObjectDoesNotExist:
        status = None  # If loan application does not exist

    def get_progress_percentage(status):
        if status == "Application Started":
            return 1  # Step 1
        elif status == "Completed":
            return 3  # Step 3
        elif status == "Rejected":
            return 3
        else:
            return 2  # Default progress step

    progress_step = get_progress_percentage(status)
    print(f"Progress step: {progress_step}")  # Debug statement
    
    context = {
        'user': user,
        'username': username,
        'progress_step': progress_step,
        'status': status,
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