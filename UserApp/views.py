from django.shortcuts import render
from django.http import HttpResponse
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


import logging

logger = logging.getLogger(__name__)


def register(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserForm()

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
                user, user_type = admin, 'admin'
        except AdminModel.DoesNotExist:
            pass

        # Check Franchise
        if not user:
            try:
                franchise = Franchise.objects.get(email=identifier)

                if check_password(password, franchise.password):
                    if franchise.payment_status:  # ✅ Corrected Boolean check
                        request.session.flush()
                        request.session['user_id'] = str(franchise.pk)
                        request.session['user_type'] = 'franchise'

                        # Remove old session flags
                        request.session.pop('requires_payment', None)

                        request.session.set_expiry(
                            3600)  # 1-hour session expiry
                        logger.info(
                            f"Franchise login successful (ID: {franchise.pk})")
                        return redirect('/franchise_dashboard')

                    # If payment is not active, redirect to payment confirmation page
                    request.session['franchise_id'] = str(franchise.pk)
                    request.session['requires_payment'] = True
                    return redirect('payment_redirect')

            except Franchise.DoesNotExist:
                pass

        # Check Staff
        if not user:
            try:
                staff = StaffModel.objects.get(email=identifier)
                # ⚠️ Only if passwords are not hashed (Fix ASAP)
                if password == staff.password:
                    user, user_type = staff, 'staff'
            except StaffModel.DoesNotExist:
                pass

        # Check Executive
        if not user:
            try:
                executive = UserModel.objects.get(email=identifier)
                if check_password(password, executive.password):
                    user, user_type = executive, 'executive'
            except UserModel.DoesNotExist:
                pass

        # **Login Handling**
        if user:
            request.session.flush()  # Clear old session
            request.session['user_id'] = str(user.pk)
            request.session['user_type'] = user_type
            request.session.set_expiry(3600)  # 1-hour session expiry

            logger.info(f"Login successful: {user_type} (ID: {user.pk})")

            # **Redirect based on user type**
            if user_type == 'admin':
                return redirect('/')
            elif user_type == 'franchise':
                return redirect('/franchise_dashboard')
            elif user_type == 'staff':
                return redirect('/dashboard')
            elif user_type == 'executive':
                return redirect(f'/index/{user.pk}')
        else:
            error = "Invalid credentials. Please try again."
            logger.warning(f"Login failed for identifier: {identifier}")
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'login.html', {'error': error})


def payment_redirect(request):
    """
    Render a page with UPI payment instructions and auto-redirect using JavaScript.
    """
    # Verify session data
    franchise_id = request.session.get('franchise_id')
    requires_payment = request.session.get('requires_payment', False)

    if not franchise_id or not requires_payment:
        return redirect('login')

    # UPI Payment Deep Link
    upi_id = '8138911511@ybl'
    payment_amount = 500  # Example amount
    payment_note = 'Franchise Membership Payment'

    upi_link = f"upi://pay?pa={upi_id}&pn=Franchise&mc=&tid=&tr=&tn={payment_note}&am={payment_amount}&cu=INR"

    context = {
        'upi_link': upi_link
    }

    return render(request, 'payment_redirect.html', context)


def payment_confirmation(request):
    franchise_id = request.session.get('franchise_id')

    if not franchise_id:
        return redirect('login')

    if request.method == 'POST':
        screenshot = request.FILES.get('payment_screenshot')
        transaction_id = request.POST.get('transaction_id', str(
            uuid.uuid4()))  # Generate random ID if not provided

        try:
            franchise = Franchise.objects.get(pk=franchise_id)

            # Create a payment entry
            payment = Payment.objects.create(
                franchise=franchise,
                transaction_id=transaction_id,
                payment_screenshot=screenshot,
                status='pending'  # Admin verifies manually
            )

            # Mark franchise as pending verification
            franchise.payment_status = False
            franchise.save()

            messages.success(
                request, "Payment receipt uploaded! We will verify it soon.")
            # Redirect to user dashboard
            return redirect('/franchise_dashboard')

        except Franchise.DoesNotExist:
            messages.error(request, "Franchise not found.")

    return redirect('/franchise_dashboard')


def home(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    user_type = request.session.get('user_type', None)

    # If user is admin
    if user_type == 'admin':
        try:
            admin = AdminModel.objects.get(admin_id=user_id)
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name if admin.admin_last_name else ''}"
        except AdminModel.DoesNotExist:
            return redirect('/login')

        today = datetime.now().date()
        all_loans = LoanApplicationModel.objects.filter(followup_date=today)
        loan_followup = all_loans.filter(assigned_to=user_id)

        # Count the number of franchises
        all_franchises = Franchise.objects.all()
        franchise_count = all_franchises.count()

        # Count the number of staff
        all_staff = StaffModel.objects.all()
        staff_count = all_staff.count()

        loan_app = LoanApplicationModel.objects.all()
        loan_app_count = loan_app.count()
        last_loan_app = loan_app.order_by('-form_id')[:10]

        login_success = request.GET.get('login_success') == 'true'

        context = {
            'username': admin_name,
            'forms': last_loan_app,
            'loans': all_loans,
            'total_franchise_count': franchise_count,
            'total_staff_count': staff_count,
            'loan_app_count': loan_app_count,
            'all_franchises': all_franchises,
            'all_staff': all_staff,
            'admin': admin,
            'login_success': login_success,
            'can_add_loan': True  # Admin can add loans
        }
        return render(request, 'index.html', context)

    # If user is franchise
    elif user_type == 'franchise':
        try:
            franchise = Franchise.objects.get(franchise_id=user_id)
        except Franchise.DoesNotExist:
            return redirect('/login')
        franchise_wallets = Franchise.objects.values(
            'franchise_name', 'wallet_balance')

        franchise_name = f"{franchise.franchise_name if franchise.franchise_name else ''}"

        # Fetch all loans related to this franchise
        related_loans = LoanApplicationModel.objects.filter(
            franchise=franchise)
        loan_count = related_loans.count()

        # Count the number of other franchises
        all_franchises = Franchise.objects.all()
        franchise_count = all_franchises.count()

        context = {
            'username': franchise_name,
            'franchise': franchise,
            'related_loans': related_loans,
            'loan_count': loan_count,
            'franchise_wallets': franchise_wallets,
            'can_add_loan': True  # Franchise can add loans
        }
        return render(request, 'franchise_dashboard.html', context)

    # If user is staff
    elif user_type == 'staff':
        try:
            staff = StaffModel.objects.get(staff_id=user_id)
        except StaffModel.DoesNotExist:
            return redirect('/login')

        staff_name = f"{staff.first_name} {staff.last_name if staff.last_name else ''}"

        # Redirect to profile update if profile is not completed
        if not staff.profile_completed:
            return redirect('update_profile')

        # Count the number of franchises
        all_franchises = Franchise.objects.all()
        franchise_count = all_franchises.count()

        # Fetch all loans
        all_loans = LoanApplicationModel.objects.all()
        loan_app_count = all_loans.count()

        context = {
            'username': staff_name,
            'admin': staff,
            'all_loans': all_loans,
            'loan_app_count': loan_app_count,
            'all_franchises': all_franchises,
            'franchise_count': franchise_count,
            'can_add_loan': True  # Staff can add loans
        }

        return render(request, 'dashboard.html', context)

    # If user is the 4th type (other user type, who is not admin, franchise, or sta

    # If no valid user type
    return redirect('/login')


def other_user_dashboard(request, user_id):
    try:
        # This should be correct since you use 'id' for the UserModel
        other_user = UserModel.objects.get(user_id=user_id)
        other_user_name = f"{other_user.name} "
    except UserModel.DoesNotExist:
        return redirect('/login')

    # Check if 'other_user' is a StaffModel, and get the related staff instance
    try:
        # Or use 'user_id' if that's how it's related
        staff_member = StaffModel.objects.get(email=other_user.email)
    except StaffModel.DoesNotExist:
        staff_member = None

    # Fetch loans related to this user (checking the staff member)
    related_loans = LoanApplicationModel.objects.filter(
        assigned_to=staff_member)  # Use 'assigned_to' to filter by staff
    loan_count = related_loans.count()

    # Count the number of franchises
    all_franchises = Franchise.objects.all()
    franchise_count = all_franchises.count()

    context = {
        'username': other_user_name,
        'other_user': other_user,
        'related_loans': related_loans,
        'loan_count': loan_count,
        'franchise_count': franchise_count,
        'can_add_loan': True  # 4th type user can add loans
    }

    return render(request, 'home.html', context)


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
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=staff)  # Use staff directly
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
            form = StaffModelForm(request.POST, request.FILES)
            if form.is_valid():
                staff = form.save(commit=False)
                staff.save()  # Save staff with all details
                messages.success(request, "Staff member added successfully!")
                return redirect('/')  # Redirect after successful creation
            else:
                messages.error(request, "There was an error in the form. Please correct it.")

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
