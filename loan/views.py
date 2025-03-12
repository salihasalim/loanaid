from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from datetime import datetime

from UserApp.models import *
from UserApp.forms import *


def loanform(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"
        loan = LoanModel.objects.all()
        status = StatusModel.objects.all()
        bank = BankModel.objects.all()
        
        if request.method == 'POST':
            files = request.FILES.getlist('files')  # Get list of files uploaded
            form = LoanApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                loan_form = form.save()  # Save the form
                # Save uploaded files associated with the form
                for file in files:
                    UploadedFile.objects.create(
                        file=file,
                        loan_application=LoanApplicationModel.objects.get(form_id=loan_form.form_id)
                    )
                return redirect('/')  # Redirect to home after successful form submission
        else:
            form = LoanApplicationForm()  # Initialize form for GET request
            
        return render(request, 'loan-form.html', {
            'username': admin_name,
            'admin': admin,
            'loan': loan,
            'status': status,
            'bank': bank,
            'form': form
        })


def loan_page(request, form_id):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"
        
        form_instance = get_object_or_404(LoanApplicationModel, form_id=form_id)
        files = UploadedFile.objects.filter(loan_application=form_instance)

        if request.method == 'POST':
            form = LoanApplicationForm(request.POST, instance=form_instance)
            if request.POST.get('submit-form'):
                # Superadmin-specific form fields
                if admin.is_superadmin:
                    form_instance.first_name = request.POST.get('first_name')
                    form_instance.last_name = request.POST.get('last_name')
                    form_instance.district = request.POST.get('district')
                    form_instance.place = request.POST.get('place')
                    form_instance.phone_no = request.POST.get('phone_no')
                    form_instance.loan_name = LoanModel.objects.get(loan_id=request.POST.get('loan_name'))
                    form_instance.loan_amount = request.POST.get('loan_amount')
                    form_instance.bank_name = BankModel.objects.get(bank_id=request.POST.get('bank_name'))
                    form_instance.executive_name = request.POST.get('executive_name')
                    form_instance.mobileno_1 = request.POST.get('mobileno_1')
                    form_instance.mobileno_2 = request.POST.get('mobileno_2')
                    form_instance.followup_date = request.POST.get('followup_date')
                    form_instance.description = request.POST.get('description')
                    form_instance.status_name = StatusModel.objects.get(status_id=request.POST.get('status_name'))
                    form_instance.application_description = request.POST.get('application_description')

                else:
                    form_instance.followup_date = request.POST.get('followup_date')
                    form_instance.description = request.POST.get('description')
                    form_instance.status_name = StatusModel.objects.get(status_id=request.POST.get('status_name'))
                    form_instance.application_description = request.POST.get('application_description')

                form_instance.save()  # Save the updated form

            # Handle file uploads for new files
            if request.POST.get('new_files'):
                files = request.FILES.getlist('uploaded_files')
                formid = request.POST.get('form_id')
                for file in files:
                    UploadedFile.objects.create(
                        file=file,
                        loan_application=LoanApplicationModel.objects.get(form_id=formid)
                    )
                return redirect('loan-page', form_id)

        else:
            form = LoanApplicationForm(instance=form_instance)
            files = UploadedFile.objects.filter(loan_application=form_instance)

        return render(request, 'loan-page.html', {
            'username': admin_name,
            'admin': admin,
            'form': form,
            'files': files
        })


def loan_application_status(request):
    user_phone = request.GET.get('phone_no')
    loan_application = get_object_or_404(LoanApplicationModel, phone_no=user_phone)
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


def all_app(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        loan_app = LoanApplicationModel.objects.all()
        admin = AdminModel.objects.get(admin_id=user)
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"
        return render(request, 'all-files.html', {
            'username': admin_name,
            'admin': admin,
            'forms': loan_app
        })


def addloan(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
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
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
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
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        all_bank = BankModel.objects.all()
        if request.method == 'POST':
            form = BankForm(request.POST)
            if form.is_valid():
                form.save()  # Save new bank
                return redirect('addbank')
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
