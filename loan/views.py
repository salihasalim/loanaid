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
            files = request.FILES.getlist('files')
            form = LoanApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                loan_form = form.save()
                for file in files:
                    UploadedFile.objects.create(
                        file=file,
                        loan_application=LoanApplicationModel.objects.get(
                            form_id=loan_form.form_id)
                    )
                return redirect('/')

        else:
            form = LoanApplicationForm()
        return render(request, 'loan-form.html', {'username': admin_name, 'admin': admin, 'loan': loan, 'status': status, 'bank': bank, 'form': form})


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
        # Get the specific form entry by ID
        form_instance = get_object_or_404(
            LoanApplicationModel, form_id=form_id)
        files = UploadedFile.objects.filter(loan_application=form_instance)

        # Check if the form was submitted
        if request.method == 'POST':

            form = LoanApplicationForm(request.POST, instance=form_instance)
            if request.POST.get('submit-form'):

                if admin.is_superadmin:
                    first_name = request.POST.get('first_name')
                    last_name = request.POST.get('last_name')
                    district = request.POST.get('district')
                    place = request.POST.get('place')
                    phone_no = request.POST.get('phone_no')
                    loan_name = request.POST.get('loan_name')
                    loan_amount = request.POST.get('loan_amount')
                    bank_name = request.POST.get('bank_name')
                    executive_name = request.POST.get('executive_name')
                    mobileno_1 = request.POST.get('mobileno_1')
                    mobileno_2 = request.POST.get('mobileno_2')
                    followup_date = request.POST.get('followup_date')
                    description = request.POST.get('description')
                    status_name = request.POST.get('status_name')
                    application_description = request.POST.get(
                        'application_description')
                    assigned_to = request.POST.getlist('assigned_to')

                    form_instance.first_name = first_name
                    form_instance.last_name = last_name
                    form_instance.district = district
                    form_instance.place = place
                    form_instance.phone_no = phone_no
                    if loan_name:
                        form_instance.loan_name = LoanModel.objects.get(
                            loan_id=loan_name)
                    if loan_amount:
                        form_instance.loan_amount = loan_amount
                    else:
                        form_instance.loan_amount = 0
                    if followup_date:
                        form_instance.followup_date = followup_date
                    form_instance.description = description
                    if status_name:
                        form_instance.status_name = StatusModel.objects.get(
                            status_id=status_name)
                    form_instance.application_description = application_description
                    if bank_name:
                        form_instance.bank_name = BankModel.objects.get(
                            bank_id=bank_name)
                    form_instance.executive_name = executive_name
                    form_instance.mobileno_1 = mobileno_1
                    form_instance.mobileno_2 = mobileno_2
                    if assigned_to:
                        form_instance.assigned_to.set(
                            AdminModel.objects.filter(admin_id__in=assigned_to))

                else:
                    followup_date = request.POST.get('followup_date')
                    description = request.POST.get('description')
                    status_name = request.POST.get('status_name')
                    application_description = request.POST.get(
                        'application_description')
                    if followup_date:
                        form_instance.followup_date = followup_date
                    form_instance.description = description
                    if status_name:
                        form_instance.status_name = StatusModel.objects.get(
                            status_id=status_name)
                    form_instance.application_description = application_description

                form_instance.save()

            # Redirect to a success page
            if request.POST.get('new_files'):
                files = request.FILES.getlist('uploaded_files')
                formid = request.POST.get('form_id')

                for file in files:
                    UploadedFile.objects.create(
                        file=file,
                        loan_application=LoanApplicationModel.objects.get(
                            form_id=formid)
                    )
                return redirect('loan-page', form_id)

        else:
            form = LoanApplicationForm(instance=form_instance)
            files = UploadedFile.objects.filter(loan_application=form_instance)
        return render(request, 'loan-page.html', {'username': admin_name, 'admin': admin, 'form': form, 'files': files})


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
        return render(request, 'all-files.html', {'username': admin_name, 'admin': admin, 'forms': loan_app})


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
                form.save()
                # Redirect to login page after successful registration
                return redirect('/')
        else:
            form = LoanForm()
        return render(request, 'add-loan.html', {'username': admin_name, 'admin': admin, 'form': form, 'allloans': all_loans})


def addstatus(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"

        all_status = StatusModel.objects.all()
        if request.method == 'POST':
            form = StatusForm(request.POST)
            if form.is_valid():
                form.save()
                # Redirect to login page after successful registration
                return redirect('/')
        else:
            form = StatusForm()
        return render(request, 'add-status.html', {'username': admin_name, 'admin': admin, 'form': form, 'allstatus': all_status})


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
                form.save()
                # Redirect to login page after successful registration
                return redirect('addbank')
        else:
            form = BankForm()
        return render(request, 'add-bank.html', {'username': admin_name, 'admin': admin, 'form': form, 'allbank': all_bank})


def delete_loan(request, loan_id):
    loan = get_object_or_404(LoanModel, pk=loan_id)
    if request.method == 'POST':
        loan.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('addloan')
    return redirect('addloan')


def delete_status(request, status_id):
    status = get_object_or_404(StatusModel, pk=status_id)
    if request.method == 'POST':
        status.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('addstatus')
    return redirect('addstatus')


def delete_bank(request, bank_id):
    bank = get_object_or_404(BankModel, pk=bank_id)
    if request.method == 'POST':
        bank.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('addbank')
    return redirect('addbank')


def delete_user(request, admin_id):
    user = get_object_or_404(AdminModel, pk=admin_id)
    if request.method == 'POST':
        LoanApplicationModel.objects.filter(
            assigned_to=user).update(assigned_to=None)
        user.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('/')
    return redirect('/')


def delete_loanpage(request, form_id):
    loan = get_object_or_404(LoanApplicationModel, pk=form_id)
    if request.method == 'POST':
        loan.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('/')
    return redirect('/')
