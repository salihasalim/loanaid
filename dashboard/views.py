from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.template.context_processors import request

from UserApp.models import *
from UserApp.forms import *


def dashboard(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')

    admin = UserModel.objects.get(user_id=user)
    if admin.user_last_name:
        admin_name = f"{admin.user_first_name} {admin.user_last_name}"
    else:
        admin_name = f"{admin.user_first_name}"
    phoneno = admin.user_phoneno
    try:
        loan_application = LoanApplicationModel.objects.get(phone_no=phoneno)
        status = loan_application.status_name.status_name if loan_application.status_name else "Application Started"
    except ObjectDoesNotExist:
        # If the loan application does not exist, set status to None or a default value
        status = None

    def get_progress_percentage(status):
        if status == "Application Started":
            return 1  # Step 1
        elif status == "Completed":
            return 3  # Step 3
        elif status == "Rejected":
            return 3
        else:
            return 2

    progress_step = get_progress_percentage(status)
    print(progress_step)
    context = {
        'admin': admin,
        'username': admin_name,
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