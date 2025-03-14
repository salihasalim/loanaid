from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from datetime import datetime

from UserApp.models import *
from UserApp.forms import *


def loanform(request):
    # Retrieve user ID from session
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    try:
        # Retrieve user object based on user_id stored in session
        admin = AdminModel.objects.get(pk=user_id)
    except AdminModel.DoesNotExist:
        return redirect('/login')

    # Determine the admin name
    admin_name = f"{admin.admin_first_name} {admin.admin_last_name}" if admin.admin_last_name else f"{admin.admin_first_name}"

    # Check user type and filter loan applications accordingly
    if admin.is_superadmin:
        loan = LoanModel.objects.all()  # Superadmins see all loans
    elif admin.is_staff:
        # Staff can only see loans connected to their assigned franchises
        connected_franchises = Franchise.objects.filter(staff=admin)
        loan = LoanModel.objects.filter(franchise__in=connected_franchises)
    else:
        # Franchises only see their own loans
        loan = LoanModel.objects.filter(franchise=admin)

    status = StatusModel.objects.all()
    bank = BankModel.objects.all()

    if request.method == 'POST':
        files = request.FILES.getlist('files')
        form = LoanApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            loan_form = form.save(commit=False)

            if not admin.is_superadmin and not admin.is_staff:
                loan_form.franchise = admin 

            loan_form.save()

            # Save uploaded files
            for file in files:
                UploadedFile.objects.create(
                    file=file,
                    loan_application=loan_form
                )

            return redirect('/')  # Redirect after saving

    else:
        form = LoanApplicationForm()

    return render(request, 'loan-form.html', {
        'username': admin_name,
        'admin': admin,
        'loan': loan,
        'status': status,
        'bank': bank,
        'form': form
    })



def loan_page(request, form_id):
    # Get user_id from session (changed from 'user' to 'user_id')
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    # Get the admin object based on the user_id
    admin = AdminModel.objects.get(admin_id=user_id)

    # Get the loan application
    form_instance = get_object_or_404(LoanApplicationModel, form_id=form_id)

    # Restrict access based on user type
    if admin.is_superadmin:
        pass  # Superadmins can access everything
    elif admin.is_staff:
        # Staff can only access loans connected to their franchises
        connected_franchises = Franchise.objects.filter(staff=admin)
        if form_instance.franchise not in connected_franchises:
            return redirect('/')  # Redirect if unauthorized
    else:
        # Franchises can only access their own loans
        if form_instance.franchise != admin:
            return redirect('/')  # Redirect if unauthorized

    admin_name = f"{admin.admin_first_name} {admin.admin_last_name}" if admin.admin_last_name else f"{admin.admin_first_name}"
    files = UploadedFile.objects.filter(loan_application=form_instance)

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, instance=form_instance)

        if request.POST.get('submit-form'):
            # Superadmins can edit all fields
            if admin.is_superadmin:
                form_instance.first_name = request.POST.get('first_name')
                form_instance.last_name = request.POST.get('last_name')
                form_instance.district = request.POST.get('district')
                form_instance.place = request.POST.get('place')
                form_instance.phone_no = request.POST.get('phone_no')
                form_instance.loan_name = LoanModel.objects.get(
                    loan_id=request.POST.get('loan_name'))
                form_instance.loan_amount = request.POST.get('loan_amount')
                form_instance.bank_name = BankModel.objects.get(
                    bank_id=request.POST.get('bank_name'))
                form_instance.executive_name = request.POST.get(
                    'executive_name')
                form_instance.mobileno_1 = request.POST.get('mobileno_1')
                form_instance.mobileno_2 = request.POST.get('mobileno_2')
                form_instance.followup_date = request.POST.get('followup_date')
                form_instance.description = request.POST.get('description')
                form_instance.status_name = StatusModel.objects.get(
                    status_id=request.POST.get('status_name'))
                form_instance.application_description = request.POST.get(
                    'application_description')

            # Staff & Franchises can only update specific fields
            else:
                form_instance.followup_date = request.POST.get('followup_date')
                form_instance.description = request.POST.get('description')
                form_instance.status_name = StatusModel.objects.get(
                    status_id=request.POST.get('status_name'))
                form_instance.application_description = request.POST.get(
                    'application_description')

            form_instance.save()

        # Handle file uploads
        if request.POST.get('new_files'):
            files = request.FILES.getlist('uploaded_files')
            for file in files:
                UploadedFile.objects.create(
                    file=file,
                    loan_application=form_instance
                )
            return redirect('loan-page', form_id)

    else:
        form = LoanApplicationForm(instance=form_instance)

    return render(request, 'loan-page.html', {
        'username': admin_name,
        'admin': admin,
        'form': form,
        'files': files
    })



def all_app(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    admin = AdminModel.objects.get(admin_id=user_id)

    # Remaining code here...


    admin_name = f"{admin.admin_first_name} {admin.admin_last_name}" if admin.admin_last_name else f"{admin.admin_first_name}"

    if admin.is_superadmin:
        loan_app = LoanApplicationModel.objects.all()
    elif admin.is_staff:
        connected_franchises = Franchise.objects.filter(staff=admin)
        loan_app = LoanApplicationModel.objects.filter(franchise__in=connected_franchises)
    else:
        loan_app = LoanApplicationModel.objects.filter(franchise=admin)

    return render(request, 'all-files.html', {
        'username': admin_name,
        'admin': admin,
        'forms': loan_app
    })



def loan_application_status(request):
    user_phone = request.GET.get('phone_no')
    loan_application = get_object_or_404(
        LoanApplicationModel, phone_no=user_phone)
    status = loan_application.status_name.status_name if loan_application.status_name else "Not Available"

    def get_progress_percentage(status):
        return {
            "Application Started": 33,
            "Pending": 66,
            "Completed": 100,
        }.get(status, 0)

    context = {
        'progress_percentage': get_progress_percentage(status),
        'status': status,
    }
    return render(request, 'dashboard.html', context)


def update_status(request, form_id):
    loan_form = get_object_or_404(LoanApplicationModel, form_id=form_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['Accept', 'Reject']:
            loan_form.workstatus = status
            loan_form.save()
    return redirect('/')


def addloan(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user_id)
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"
        all_loans = LoanModel.objects.all()
        if request.method == 'POST':
            form = LoanForm(request.POST)
            if form.is_valid():
                form.save()  # Save new loan
                return redirect('/')
        else:
            form = LoanForm()
        return render(request, 'add-loan.html', {
            'username': admin_name,
            'admin': admin,
            'form': form,
            'allloans': all_loans
        })


def addstatus(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user_id)
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        all_status = StatusModel.objects.all()
        if request.method == 'POST':
            form = StatusForm(request.POST)
            if form.is_valid():
                form.save()  # Save new status
                return redirect('/')
        else:
            form = StatusForm()
        return render(request, 'add-status.html', {
            'username': admin_name,
            'admin': admin,
            'form': form,
            'allstatus': all_status
        })


def addbank(request):
    # Get user_id from session (changed from 'user' to 'user_id')
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user_id)
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        all_bank = BankModel.objects.all()

        if request.method == 'POST':
            form = BankForm(request.POST)
            if form.is_valid():
                form.save()  # Save new bank
                return redirect('addbank')  # Redirect to the same page to show the updated list
        else:
            form = BankForm()

        return render(request, 'add-bank.html', {
            'username': admin_name,
            'admin': admin,
            'form': form,
            'allbank': all_bank
        })



def delete_loan(request, loan_id):
    loan = get_object_or_404(LoanModel, pk=loan_id)
    if request.method == 'POST':
        loan.delete()  # Delete loan
        return redirect('addloan')
    return redirect('addloan')


def delete_status(request, status_id):
    status = get_object_or_404(StatusModel, pk=status_id)
    if request.method == 'POST':
        status.delete()  # Delete status
        return redirect('addstatus')
    return redirect('addstatus')


def delete_bank(request, bank_id):
    bank = get_object_or_404(BankModel, pk=bank_id)
    if request.method == 'POST':
        bank.delete()  # Delete bank
        return redirect('addbank')
    return redirect('addbank')


def delete_loanpage(request, form_id):
    loan = get_object_or_404(LoanApplicationModel, pk=form_id)
    if request.method == 'POST':
        loan.delete()  # Delete loan application
        return redirect('/')
    return redirect('/')
