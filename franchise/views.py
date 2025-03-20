from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from UserApp.models import *
from UserApp.forms import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

def add_franchise(request):
    # Check if user is logged in via session
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')

    if not user_id or user_type not in ['admin', 'staff']:
        messages.error(request, "Unauthorized access. Please log in.")
        return redirect('/login/')

    if request.method == 'POST':
        form = FranchiseForm(request.POST, request.FILES)
        if form.is_valid():
            franchise = form.save(commit=False)
            plain_password = request.POST.get('password')

            # If logged-in user is staff, set the staff relation
            if user_type == 'staff':
                try:
                    staff = StaffModel.objects.get(pk=user_id)
                    franchise.staff = staff
                except StaffModel.DoesNotExist:
                    messages.error(request, "Staff user not found.")
                    return redirect('/login/')

            franchise.save()

            # Send email with franchise details
            send_mail(
                "Franchise Account Created",
                f"Hello {franchise.franchise_owner},\n\nYour franchise account has been created successfully!\n\nUsername: {franchise.email}\nPassword: {plain_password}\nReferral Code: {franchise.referral_code}\n\nPlease log in and update your password immediately.",
                "admin@yourdomain.com",
                [franchise.email],
                fail_silently=False,
            )

            messages.success(request, "Franchise added successfully and credentials sent via email.")
            return redirect("list_franchise")

    else:
        form = FranchiseForm()

    return render(request, 'add_franchise.html', {'form': form})

def list_franchise(request):
    # Check if user is logged in via session
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')

    if not user_id or user_type not in ['admin', 'staff']:
        messages.error(request, "Unauthorized access. Please log in.")
        return redirect('/login/')

    # Fetch franchises based on user type
    if user_type == 'admin':
        franchises = Franchise.objects.all()
    else:  # If staff, show only their assigned franchises
        franchises = Franchise.objects.filter(staff_id=user_id)

    return render(request, 'list_franchise.html', {'franchises': franchises})


# Franchise dashboard view
def franchise_dashboard(request):
    franchise_id = request.session.get('franchise_id')
    if not franchise_id:
        return redirect("franchise_login")
    
    franchise = get_object_or_404(Franchise, franchise_id=franchise_id)
    return render(request, 'franchise/dashboard.html', {'franchise': franchise})

# Edit franchise profile
def franchise_edit(request):
    franchise_id = request.session.get('franchise_id')
    if not franchise_id:
        return redirect("franchise_login")
    
    franchise = get_object_or_404(Franchise, franchise_id=franchise_id)
    if request.method == 'POST':
        form = FranchiseForm(request.POST, request.FILES, instance=franchise)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("franchise_dashboard")
    else:
        form = FranchiseForm(instance=franchise)

    return render(request, 'franchise/edit_profile.html', {'form': form})

# Franchise logout
def franchise_logout(request):
    request.session.flush()  # Clear the session
    messages.success(request, "Logged out successfully.")
    return redirect("franchise_login")


def staff_uploaded(request):
    print("Session Data in staff_uploaded view:", request.session.items())  # Debugging session data

    # Check if user is logged in and is an admin
    user_type = request.session.get('user_type')
    if user_type != 'admin':
        print("User is not admin, redirecting to login")
        return redirect('/login')  # Redirect to login if not an admin

    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login')

    # Assuming the admin object is related to 'user_id'
    admin = get_object_or_404(AdminModel, admin_id=user_id)
    admin_name = f"{admin.admin_first_name} {admin.admin_last_name}" if admin.admin_last_name else admin.admin_first_name

    # Your form and staff assignment logic
    if request.method == 'POST':
        form = StaffAssignmentForm(request.POST)
        if form.is_valid():
            staff_assignment = form.save(commit=False)
            staff_assignment.created_at = timezone.now()
            staff_assignment.assigned_by = admin  # Set the admin assigning the staff
            staff_assignment.save()

            messages.success(request, "Staff assignment uploaded successfully.")
            return redirect('/')  # Redirect to a proper page (dashboard, etc.)
    else:
        form = StaffAssignmentForm()

    return render(request, 'assign_assignment.html', {'form': form, 'username': admin_name})



# View all staff assignments (admin functionality)
def all_assignments(request):
    user = request.session.get('user', None)
    if not user:
        return redirect('/login')

    admin = get_object_or_404(AdminModel, admin_id=user)
    admin_name = f"{admin.admin_first_name} {admin.admin_last_name}" if admin.admin_last_name else admin.admin_first_name

    # Filter assignments based on admin privileges
    if admin.is_superadmin:
        assignments = StaffAssignmentModel.objects.all()
    else:
        assignments = StaffAssignmentModel.objects.filter(assign_to=admin)

    all_staff = AdminModel.objects.filter(is_superadmin=False)
    return render(request, 'staff_assignments.html', {'assignments': assignments, 'admin': admin, 'username': admin_name, 'all_staff': all_staff})

# Update staff assignment
def update_assignment(request, assignment_id):
    if request.method == 'POST':
        assigned_to_id = request.POST.get('assigned_to')
        try:
            assignment = StaffAssignmentModel.objects.get(assignment_id=assignment_id)
            if assigned_to_id:
                assignment.assign_to = AdminModel.objects.get(admin_id=assigned_to_id)
            else:
                assignment.assign_to = None
            assignment.save()
            messages.success(request, "Staff assignment updated successfully.")
        except StaffAssignmentModel.DoesNotExist:
            messages.error(request, "Assignment not found.")
    
    return redirect('staff_assignments')

