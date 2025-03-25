from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth.hashers import check_password
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from UserApp.models import *
from UserApp.forms import *
from dashboard.views import *
from datetime import datetime
from django.shortcuts import render, redirect
from .models import StaffModel, LoanApplicationModel
from django.contrib import messages
from django.urls import reverse


def home(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    user_type = request.session.get('user_type', None)
    
    if user_type == 'admin':
        admin = AdminModel.objects.get(admin_id=user_id)
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name if admin.admin_last_name else ''}"

        loan_form = LoanApplicationModel.objects.filter(assigned_to=user_id)
        accepted_loans = loan_form.filter(workstatus='Accept')
        new_loans = loan_form.filter(workstatus='Not selected')
        accepted_loans_count = accepted_loans.count()

        today = datetime.now().date()
        all_loans = LoanApplicationModel.objects.filter(followup_date=today, workstatus='Accept')
        loan_followup = all_loans.filter(assigned_to=user_id)

        all_staff = StaffModel.objects.all()
        all_staff_count = all_staff.count()

        loan_app = LoanApplicationModel.objects.all()
        loan_app_count = loan_app.count()
        last_loan_app = loan_app.order_by('-form_id')[:10]

        login_success = request.GET.get('login_success') == 'true'

        if admin.is_superadmin:
            context = {
                'username': admin_name,
                'forms': last_loan_app,
                'loans': all_loans,
                'total_staff_count': all_staff_count,
                'loan_app_count': loan_app_count,
                'all_staff': all_staff,
                'admin': admin,
                'login_success': login_success
            }
        else:
            context = {
                'username': admin_name,
                'forms': accepted_loans,
                'new_loans': new_loans,
                'loans': loan_followup,
                'total_staff_count': all_staff_count,
                'loan_app_count': accepted_loans_count,
                'admin': admin,
                'login_success': login_success
            }
        return render(request, 'index.html', context)

    elif user_type == 'staff':
        try:
            staff = StaffModel.objects.get(staff_id=user_id)
        except StaffModel.DoesNotExist:
            return redirect('/login')

        admin_name = f"{staff.first_name} {staff.last_name if staff.last_name else ''}"
        
        if not staff.profile_completed:
            return redirect('profile_update')

        all_loans = LoanApplicationModel.objects.all()
        all_franchises = Franchise.objects.all()
        franchise_count = all_franchises.count()

        context = {
            'username': admin_name,
            'admin': staff,
            'all_loans': all_loans,
            'all_franchises': all_franchises,
            'franchise_count': franchise_count,
        }

        return render(request, 'dashboard.html', context)


    return redirect('/login')


def register(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.admin_password = make_password(
                form.cleaned_data['admin_password'])  # Hash password
            admin.save()
            # Redirect to login after successful registration
            return redirect('login')
    else:
        form = AdminForm()

    return render(request, 'register.html', {'form': form})


def login(request):
    error = None
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
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
                if password == staff.password:
                    user = staff
                    user_type = 'staff'
            except StaffModel.DoesNotExist:
                pass

        if user:
            request.session['user_id'] = user.pk
            request.session['user_type'] = user_type
            request.session.set_expiry(3600)

            if user_type == 'admin':
                return redirect('/')
            elif user_type == 'franchise':
                return redirect('')
            else:
                return redirect('/dashboard')

        else:
            error = "Invalid credentials"

    return render(request, 'login.html', {'error': error})



def logout_view(request):  # Change function name
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_type' in request.session:
        del request.session['user_type']

    django_logout(request)  # Call Django’s actual logout function
    request.session.flush()  # Ensure session is cleared

    return redirect('/')


def update_profile(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    staff = StaffModel.objects.get(staff_id=user_id)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=staff)  # Use staff directly
        if form.is_valid():
            form.save()
            staff.profile_completed = True  # Mark the profile as completed
            staff.save()
            return redirect('/')
    else:
        form = ProfileUpdateForm(instance=staff)  # Use staff directly

    return render(request, 'profile_update.html', {'form': form, 'username': f"{staff.first_name} {staff.last_name}"})



def create_staff(request):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('/login')

    try:
        admin = AdminModel.objects.get(admin_id=user_id)
        if not admin.is_superadmin:
            return redirect('/')  # Redirect non-admin users

        if request.method == 'POST':
            # Include files for uploads
            form = StaffModelForm(request.POST, request.FILES)
            if form.is_valid():
                staff = form.save(commit=False)
                staff.save()  # Save staff with all details
                messages.success(request, "Staff member added successfully!")
                return redirect('/')  # Redirect after successful creation
            else:
                messages.error(
                    request, "There was an error in the form. Please correct it.")

        else:
            form = StaffModelForm()

        return render(request, 'create-staff.html', {'form': form})

    except AdminModel.DoesNotExist:
        return redirect('/login')  # Handle case where admin doesn't exist


def view_staffs(request, staff_id):
    user_id = request.session.get('user_id')
    if user_id is None:
        return redirect('/login')

    try:
        admin = AdminModel.objects.get(admin_id=user_id)
        admin_name = f"{admin.admin_first_name} {admin.admin_last_name or ''}".strip()

        # Fetch staff details
        staff_member = get_object_or_404(StaffModel, pk=staff_id)

        return render(request, 'staff_detail.html', {
            'staff_member': staff_member,
            'admin_name': admin_name
        })

    except AdminModel.DoesNotExist:
        messages.error(request, "Admin not found. Please log in again.")
        return redirect('/login')


def list_staff(request):
    all_staff = StaffModel.objects.all()
    context = {'all_staff': all_staff}
    return render(request, 'all_staffs.html', context)


def delete_staff(request, staff_id):
    staff_member = get_object_or_404(StaffModel, pk=staff_id)

    if request.method == 'POST':
        LoanApplicationModel.objects.filter(
            assigned_to=staff_member).update(assigned_to=None)

        staff_member.delete()

        return redirect('/')
    return redirect('/')


def delete_files(request, id):
    file = get_object_or_404(UploadedFile, pk=id)
    loan_id = file.loan_application.form_id
    if request.method == 'POST':
        file.delete()
        # Adjust the redirect based on your URL name for the user list page
        return redirect('loan-page', loan_id)
    return redirect('loan-page', loan_id)
