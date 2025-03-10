from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from datetime import datetime

from UserApp.models import *
from UserApp.forms import *

# Admin can add franchises
def admin_add_franchise(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admins can add franchises.")
        return redirect("dashboard")

    if request.method == 'POST':
        form = FranchiseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Franchise added successfully.")
            return redirect("franchise_list")
    else:
        form = FranchiseForm()

    return render(request, 'admin/add_franchise.html', {'form': form})

# Franchise login
def franchise_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            franchise = Franchise.objects.get(email=email)
            if check_password(password, franchise.password):
                request.session['franchise_id'] = str(franchise.franchise_id)
                messages.success(request, "Login successful.")
                return redirect("franchise_dashboard")
            else:
                messages.error(request, "Invalid credentials.")
        except Franchise.DoesNotExist:
            messages.error(request, "Franchise not found.")
    return render(request, 'franchise/login.html')

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

# Staff assignment upload (admin functionality)
def staff_uploaded(request):
    user = request.session.get('user', None)
    if not user:
        return redirect('/login')

    admin = get_object_or_404(AdminModel, admin_id=user)
    admin_name = f"{admin.admin_first_name} {admin.admin_last_name}" if admin.admin_last_name else admin.admin_first_name

    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff_assignment = form.save(commit=False)
            staff_assignment.created_at = datetime.now()
            staff_assignment.assigned_by = admin
            staff_assignment.save()
            messages.success(request, "Staff assignment uploaded successfully.")
            return redirect('/')  # Redirect to another page if necessary
    else:
        form = StaffForm()

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

