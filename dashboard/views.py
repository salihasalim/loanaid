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