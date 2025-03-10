from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from .models import *


class AdminForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Confirm Password",
            }
        ),
        required=True,
    )

    class Meta:
        model = AdminModel
        fields = [
            "admin_first_name",
            "admin_last_name",
            "admin_email",
            "admin_phone",
            "admin_password",
            "is_superadmin",
        ]
        widgets = {
            "admin_first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "First Name",
                }
            ),
            "admin_last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Last Name",
                }
            ),
            "admin_email": forms.EmailInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Email Address",
                }
            ),
            "admin_phone": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Phone Number",
                }
            ),
            "admin_password": forms.PasswordInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Password",
                }
            ),
            "is_superadmin": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_admin_email(self):
        email = self.cleaned_data.get("admin_email")
        if AdminModel.objects.filter(admin_email=email).exists():
            raise ValidationError("An admin with this email already exists.")
        return email

    def clean_admin_password(self):
        password = self.cleaned_data.get("admin_password")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password  # Don't hash it here, it's handled in the model's save method

    def clean_admin_phone(self):
        phone = self.cleaned_data.get("admin_phone")
        if phone and (len(phone) != 10 or not phone.isdigit()):
            raise ValidationError(
                "Phone Number must be exactly 10 digits and contain only numbers."
            )
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("admin_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


class StaffModelForm(forms.ModelForm):
    """Form for creating and managing staff members"""

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Confirm Password",
            }
        ),
        required=True,
    )

    class Meta:
        model = StaffModel
        fields = [
            "franchise",
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "password",
            "is_active",
        ]
        widgets = {
            "franchise": forms.Select(attrs={"class": "form-select form-control"}),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "First Name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Last Name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Email Address",
                }
            ),
            "phone_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Phone Number",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Password",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(StaffModelForm, self).__init__(*args, **kwargs)

        # If an admin user is provided, set them as the manager of the staff
        if user and isinstance(user, AdminModel):
            self.instance.managed_by = user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        instance = getattr(self, "instance", None)

        # Check if email already exists but exclude current instance if editing
        if (
            StaffModel.objects.filter(email=email)
            .exclude(pk=instance.pk if instance.pk else None)
            .exists()
        ):
            raise ValidationError("A staff member with this email already exists.")
        return email

    def clean_phone_no(self):
        phone = self.cleaned_data.get("phone_no")
        if phone and (len(phone) != 10 or not phone.isdigit()):
            raise ValidationError(
                "Phone Number must be exactly 10 digits and contain only numbers."
            )
        return phone

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password  # Don't hash it here, it's handled in the model's save method

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


class FranchiseForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Confirm Password",
            }
        ),
        required=True,
    )

    class Meta:
        model = Franchise
        fields = [
            "franchise_name",
            "franchise_owner",
            "email",
            "mobile_no",
            "password",
            "aadhar",
            "GST",
            "pan",
            "photo",
        ]
        widgets = {
            "franchise_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Franchise Name",
                }
            ),
            "franchise_owner": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Franchise Owner",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Email Address",
                }
            ),
            "mobile_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Mobile Number",
                }
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Password",
                }
            ),
            "aadhar": forms.FileInput(attrs={"class": "form-control"}),
            "GST": forms.FileInput(attrs={"class": "form-control"}),
            "pan": forms.FileInput(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        instance = getattr(self, "instance", None)

        # Check if email already exists but exclude current instance if editing
        if (
            Franchise.objects.filter(email=email)
            .exclude(pk=instance.pk if instance.pk else None)
            .exists()
        ):
            raise ValidationError("A franchise with this email already exists.")
        return email

    def clean_mobile_no(self):
        mobile = self.cleaned_data.get("mobile_no")
        if mobile and (len(mobile) != 10 or not mobile.isdigit()):
            raise ValidationError(
                "Mobile Number must be exactly 10 digits and contain only numbers."
            )
        return mobile

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password  # Don't hash it here, it's handled in the model's save method

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


class FranchiseWalletForm(forms.ModelForm):
    class Meta:
        model = FranchiseWallet
        fields = ["franchise", "balance"]
        widgets = {
            "franchise": forms.Select(attrs={"class": "form-select form-control"}),
            "balance": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Wallet Balance",
                }
            ),
        }


class WalletTransactionForm(forms.ModelForm):
    class Meta:
        model = WalletTransaction
        fields = ["wallet", "amount", "transaction_type", "description"]
        widgets = {
            "wallet": forms.Select(attrs={"class": "form-select form-control"}),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Amount",
                }
            ),
            "transaction_type": forms.Select(
                attrs={"class": "form-select form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Transaction Description",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(WalletTransactionForm, self).__init__(*args, **kwargs)

        # If a user is provided, set the appropriate processed_by field
        if user:
            if isinstance(user, AdminModel):
                self.instance.processed_by_admin = user
            elif isinstance(user, StaffModel):
                self.instance.processed_by_staff = user


class LoanApplicationForm(forms.ModelForm):
    franchise_referral = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Franchise Referral Code",
            }
        ),
    )

    class Meta:
        model = LoanApplicationModel
        fields = [
            "franchise",
            "franchise_referral",
            "first_name",
            "last_name",
            "district",
            "place",
            "phone_no",
            "guaranter_name",
            "guaranter_phoneno",
            "guaranter_job",
            "guaranter_cibil_score",
            "guaranter_cibil_issue",
            "guaranter_it_payable",
            "guaranter_years",
            "job",
            "cibil_score",
            "cibil_issue",
            "it_payable",
            "years",
            "loan_name",
            "loan_amount",
            "followup_date",
            "description",
            "status_name",
            "application_description",
            "bank_name",
            "executive_name",
            "mobileno_1",
            "mobileno_2",
            "assigned_to",
            "document_description",
            "workstatus",
        ]
        widgets = {
            "franchise": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "First Name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Last Name",
                    "required": False,
                }
            ),
            "district": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "District",
                    "required": False,
                }
            ),
            "place": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Place",
                    "required": False,
                }
            ),
            "phone_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Phone Number",
                    "required": False,
                }
            ),
            "guaranter_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Name",
                    "required": False,
                }
            ),
            "guaranter_phoneno": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Phone Number",
                    "required": False,
                }
            ),
            "guaranter_job": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Job",
                    "required": False,
                }
            ),
            "guaranter_cibil_score": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Cibil Score",
                    "required": False,
                }
            ),
            "guaranter_cibil_issue": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Cibil Issue",
                    "rows": 3,
                    "required": False,
                }
            ),
            "guaranter_years": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "guaranter_it_payable": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "job": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Job",
                    "required": False,
                }
            ),
            "cibil_score": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Cibil Score",
                    "required": False,
                }
            ),
            "cibil_issue": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Cibil Issue",
                    "rows": 3,
                    "required": False,
                }
            ),
            "years": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "it_payable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "loan_name": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "loan_amount": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Amount",
                    "required": False,
                }
            ),
            "followup_date": forms.DateInput(
                attrs={"class": "form-control form-control-user", "type": "date"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Description",
                    "rows": 3,
                    "required": False,
                }
            ),
            "status_name": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "application_description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Description",
                    "rows": 3,
                    "required": False,
                }
            ),
            "bank_name": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "executive_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Executive Name",
                    "required": False,
                }
            ),
            "mobileno_1": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Mobile No 1",
                    "required": False,
                }
            ),
            "mobileno_2": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Mobile No 2",
                    "required": False,
                }
            ),
            "assigned_to": forms.Select(
                attrs={"class": "form-select form-control", "id": "assigned_to"}
            ),
            "document_description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Description",
                    "rows": 3,
                    "required": False,
                }
            ),
            "workstatus": forms.Select(attrs={"class": "form-select form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(LoanApplicationForm, self).__init__(*args, **kwargs)

        # Make franchise_referral not required if direct franchise selection is used
        self.fields["franchise"].required = False

        # Set queryset for assigned_to to show staff members, not admins
        self.fields["assigned_to"].queryset = StaffModel.objects.filter(is_active=True)

        # Define which fields are editable by different user types
        non_editable_fields = [
            "first_name",
            "last_name",
            "district",
            "place",
            "phone_no",
            "loan_name",
            "loan_amount",
            "bank_name",
            "executive_name",
            "mobileno_1",
            "mobileno_2",
            "franchise",
            "franchise_referral",
        ]

        # If the user is staff, disable certain fields
        if user and hasattr(user, "is_superadmin") and not user.is_superadmin:
            for field in non_editable_fields:
                if field in self.fields:
                    self.fields[field].disabled = True

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get("phone_no")
        if phone_no and len(phone_no) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone_no

    def clean_mobileno_1(self):
        mobileno_1 = self.cleaned_data.get("mobileno_1")
        if mobileno_1 and len(mobileno_1) != 10:
            raise ValidationError("Mobile number must be exactly 10 digits.")
        return mobileno_1

    def clean_mobileno_2(self):
        mobileno_2 = self.cleaned_data.get("mobileno_2")
        if mobileno_2 and len(mobileno_2) != 10:
            raise ValidationError("Mobile number must be exactly 10 digits.")
        return mobileno_2

    def clean_franchise_referral(self):
        referral = self.cleaned_data.get("franchise_referral")
        franchise = self.cleaned_data.get("franchise")

        # If franchise is directly selected, referral code is not needed
        if franchise:
            return None

        # If no franchise is selected but referral code is provided, verify it exists
        if referral and not Franchise.objects.filter(referral_code=referral).exists():
            raise ValidationError("Invalid franchise referral code.")

        return referral


class LoanStatusUpdateForm(forms.ModelForm):
    """Form for updating loan application status"""

    class Meta:
        model = LoanStatusUpdateHistory
        fields = ["loan_application", "new_status", "description"]
        widgets = {
            "loan_application": forms.Select(
                attrs={"class": "form-select form-control"}
            ),
            "new_status": forms.Select(
                attrs={
                    "class": "form-select form-control",
                    "choices": LoanApplicationModel.STATUS_CHOICES,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Update Description",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(LoanStatusUpdateForm, self).__init__(*args, **kwargs)

        # If an admin or staff user is provided, set them as the updater
        if user:
            if isinstance(user, AdminModel):
                self.instance.updated_by_admin = user
            elif isinstance(user, StaffModel):
                self.instance.updated_by_staff = user

            # If staff member, only show loan applications they're assigned to
            if isinstance(user, StaffModel):
                self.fields["loan_application"].queryset = (
                    LoanApplicationModel.objects.filter(assigned_to=user)
                )


class LoanForm(forms.ModelForm):
    class Meta:
        model = LoanModel
        fields = ["loan_name", "description"]
        widgets = {
            "loan_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Loan Name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Loan Description",
                    "rows": 3,
                    "required": False,
                }
            ),
        }


class StatusForm(forms.ModelForm):
    class Meta:
        model = StatusModel
        fields = ["status_name", "description"]
        widgets = {
            "status_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Status Name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Status Description",
                    "rows": 3,
                    "required": False,
                }
            ),
        }


class BankForm(forms.ModelForm):
    class Meta:
        model = BankModel
        fields = ["bank_name"]
        widgets = {
            "bank_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Bank Name",
                }
            )
        }


class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Confirm Password",
            }
        ),
        label="Confirm Password",
    )

    class Meta:
        model = UserModel
        fields = ["user_first_name", "user_last_name", "user_phoneno", "user_password"]
        widgets = {
            "user_first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "First Name",
                }
            ),
            "user_last_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Last Name",
                }
            ),
            "user_phoneno": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Phone Number",
                }
            ),
            "user_password": forms.PasswordInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Password",
                }
            ),
        }

    def clean_user_phoneno(self):
        phoneno = self.cleaned_data.get("user_phoneno")
        instance = getattr(self, "instance", None)

        # Check if phone already exists but exclude current instance if editing
        if (
            UserModel.objects.filter(user_phoneno=phoneno)
            .exclude(pk=instance.pk if instance.pk else None)
            .exists()
        ):
            raise ValidationError("A user with this phone number already exists.")

        if len(phoneno) != 10 or not phoneno.isdigit():
            raise ValidationError(
                "Phone Number must be exactly 10 digits and contain only numbers."
            )
        return phoneno

    def clean_user_password(self):
        password = self.cleaned_data.get("user_password")
        if password and len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("user_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


class StaffAssignmentForm(forms.ModelForm):
    class Meta:
        model = StaffAssignmentModel
        fields = [
            "name",
            "district",
            "place",
            "mobile_no",
            "loan_type",
            "details",
            "assign_to",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control form-control-user", "placeholder": "Name"}
            ),
            "district": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "District",
                }
            ),
            "place": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Place",
                }
            ),
            "mobile_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Mobile No.",
                }
            ),
            "loan_type": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Loan Type",
                }
            ),
            "details": forms.Textarea(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Property Detail/Car Detail",
                    "rows": 3,
                    "required": False,
                }
            ),
            "assign_to": forms.Select(attrs={"class": "form-select form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(StaffAssignmentForm, self).__init__(*args, **kwargs)

        # Set the assigned_by field based on who is creating the assignment
        if user and isinstance(user, StaffModel):
            self.instance.assigned_by = user

        # Set the queryset for assign_to to show active staff
        self.fields["assign_to"].queryset = StaffModel.objects.filter(is_active=True)

    def clean_mobile_no(self):
        mobile = self.cleaned_data.get("mobile_no")
        if mobile and (len(mobile) != 10 or not mobile.isdigit()):
            raise ValidationError(
                "Mobile Number must be exactly 10 digits and contain only numbers."
            )
        return mobile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileUpdate
        fields = [
            "adhaar_no",
            "adhaar_img",
            "pan_no",
            "pan_img",
            "cancelled_check",
            "bank_name",
            "ifsc_code",
            "account_no",
            "branch",
        ]
        widgets = {
            "adhaar_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Aadhaar No",
                }
            ),
            "adhaar_img": forms.FileInput(
                attrs={"class": "form-control", "placeholder": "Upload Aadhaar Image"}
            ),
            "pan_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Pan No",
                }
            ),
            "pan_img": forms.FileInput(
                attrs={"class": "form-control", "placeholder": "Upload PAN Image"}
            ),
            "cancelled_check": forms.FileInput(
                attrs={"class": "form-control", "placeholder": "Upload Cancelled Check"}
            ),
            "bank_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Bank Name",
                }
            ),
            "ifsc_code": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "IFSC Code",
                }
            ),
            "account_no": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Account No",
                }
            ),
            "branch": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "Branch",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop("staff", None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        if staff:
            self.instance.staff = staff


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["loan_application", "file", "file_type"]
        widgets = {
            "loan_application": forms.Select(
                attrs={"class": "form-select form-control"}
            ),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "file_type": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "File Type/Description",
                }
            ),
        }
