from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from django.template.context_processors import request

from UserApp.models import *
from UserApp.forms import *
from dashboard.views import *

# Create your views here.


def home(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    else:
        admin = AdminModel.objects.get(admin_id=user)
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"
        loan_form = LoanApplicationModel.objects.filter(
            assigned_to=user
        )
        accepted_loans = loan_form.filter(workstatus='Accept')
        new_loans = loan_form.filter(workstatus='Not selected')
        accepted_loans_count = accepted_loans.count()

        today = datetime.now().date()
        all_loans = LoanApplicationModel.objects.filter(
            followup_date=today, workstatus='Accept')
        loan_followup = all_loans.filter(assigned_to=user)
        all_users = AdminModel.objects.filter(is_superadmin=False)
        all_users_count = all_users.count()
        loan_app = LoanApplicationModel.objects.all()
        loan_app_count = loan_app.count()
        last_loan_app = loan_app.order_by('-form_id')[:10]

        login_success = request.GET.get('login_success') == 'true'
        if admin.is_superadmin:
            context = {
                'username': admin_name,
                'forms': last_loan_app,
                'loans': all_loans,
                'total_users_count': all_users_count,
                'loan_app_count': loan_app_count,
                'all_users': all_users,
                'admin': admin,
                'login_success': login_success
            }
        else:
            if request.method == 'POST':
                # Check if the user is submitting an update for the status
                status = request.POST.get('status')

                if status in ['Accept', 'Reject']:
                    loan_form.workstatus = status
                    loan_form.save()
            context = {
                'username': admin_name,
                'forms': accepted_loans,
                'new_loans': new_loans,
                'loans': loan_followup,
                'total_users_count': all_users_count,
                'loan_app_count': accepted_loans_count,
                'admin': admin,
                'login_success': login_success
            }
        return render(request, 'index.html', context)


def login(request):
    error = None
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # Email or Phone Number
        password = request.POST.get('password')

        user = None
        user_type = None

        # Check Admin
        try:
            admin = AdminModel.objects.get(admin_email=identifier)
            if check_password(password, admin.admin_password):
                user = admin
                user_type = 'admin'
        except AdminModel.DoesNotExist:
            pass

        # Check Franchise
        if not user:
            try:
                franchise = Franchise.objects.get(email=identifier)
                if check_password(password, franchise.password):
                    user = franchise
                    user_type = 'franchise'
            except Franchise.DoesNotExist:
                pass

        # Check Staff
        if not user:
            try:
                staff = StaffModel.objects.get(email=identifier)
                if check_password(password, staff.password):
                    user = staff
                    user_type = 'staff'
            except StaffModel.DoesNotExist:
                pass

        if user:
            request.session['user_id'] = user.pk  # Store user ID
            request.session['user_type'] = user_type  # Store user type
            request.session.set_expiry(3600)  # Session expiry time (1 hour)
            
            if user_type == 'admin':
                return redirect('dashboard')
            elif user_type == 'franchise':
                return redirect('franchise_dashboard')
            elif user_type == 'staff':
                return redirect('staff_dashboard')
        else:
            error = "Invalid credentials"

    return render(request, 'login.html', {'error': error})


def register(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.admin_password = make_password(form.cleaned_data['admin_password'])  # Hash password
            admin.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = AdminForm()

    return render(request, 'register.html', {'form': form})


def logout(request):
    del request.session['user']
    return redirect('/')

  # Redirect to the main assignments page


def update_profile(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')

    admin = AdminModel.objects.get(admin_id=user)
    if admin.admin_last_name:
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
    else:
        admin_name = f"{admin.admin_first_name}"

    user_profile = ProfileUpdate.objects.get(staff=admin)
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            # Do not save yet  # Set the created_at field to now
            profile = form.save(commit=False)
            profile.staff = admin  # Set assigned_by to the current user
            profile.save()  # Now save the instance
            # Redirect to a success page or another page as needed
            return redirect('/')
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'profile_update.html', {'form': form, 'username': admin_name, 'user_profile': user_profile})


def view_staffs(request, id):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')

    admin = AdminModel.objects.get(admin_id=user)
    if admin.admin_last_name:
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
    else:
        admin_name = f"{admin.admin_first_name}"

    staff = ProfileUpdate.objects.filter(staff=id)

    return render(request, 'all_staffs.html', {'profiles': staff, 'username': admin_name})




def create_staff(request):
    user = request.session.get('user', None)
    if user is None:
        return redirect('/login')
    
    try:
        admin = AdminModel.objects.get(admin_id=user)
        # Check if the user is an admin
        if not admin.is_superadmin:
            return redirect('/')  # Redirect non-admin users to home page
            
        if admin.admin_last_name:
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
        else:
            admin_name = f"{admin.admin_first_name}"
        
        # For GET requests, create an empty form
        # For POST requests, create a form with the submitted data
        if request.method == 'POST':
            form = StaffModelForm(request.POST, user=admin)
            if form.is_valid():
                # Save the form (which will save the model)
                staff = form.save()
                
                # Create an empty profile for the new staff
                ProfileUpdate.objects.create(staff=staff)
                
                return redirect('/')
        else:
            form = StaffModelForm(user=admin)
        franchises = Franchise.objects.filter(is_active=True)
        
        return render(request, 'create-staff.html', {
            'username': admin_name, 
            'admin': admin, 
            'form': form,
            'franchises': franchises
        })
    
    except AdminModel.DoesNotExist:
        return redirect('/login')


def delete_files(request, id):
    file = get_object_or_404(UploadedFile, pk=id)
    loan_id = file.loan_application.form_id
    if request.method == 'POST':
        file.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('loan-page', loan_id)
    return redirect('loan-page', loan_id)
