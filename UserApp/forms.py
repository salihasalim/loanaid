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
            raise ValidationError(
                "Password must be at least 8 characters long.")
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
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "password",
            "is_active",
        ]
        widgets = {
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
        super().__init__(*args, **kwargs)

        # If an admin user is provided, set them as the manager of the staff
        if user and isinstance(user, AdminModel):
            self.instance.managed_by = user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        instance = self.instance  # Get current instance

        # Check if email already exists, excluding the current instance
        if StaffModel.objects.filter(email=email).exclude(pk=instance.pk).exists():
            raise ValidationError(
                "A staff member with this email already exists.")
        return email

    def clean_phone_no(self):
        phone = self.cleaned_data.get("phone_no")
        if phone and (len(phone) != 10 or not phone.isdigit()):
            raise ValidationError(
                "Phone Number must be exactly 10 digits and contain only numbers.")
        return phone

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long.")
        return password  # No hashing here

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    # Ensure password is hashed before saving the model
    def save(self, commit=True):
        staff = super().save(commit=False)
        if commit:
            staff.save()
        return staff


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffModel
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
            "adhaar_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "Aadhaar No"}),
            "adhaar_img": forms.FileInput(attrs={"class": "form-control"}),
            "pan_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "PAN No"}),
            "pan_img": forms.FileInput(attrs={"class": "form-control"}),
            "cancelled_check": forms.FileInput(attrs={"class": "form-control"}),
            "bank_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Bank Name"}),
            "ifsc_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "IFSC Code"}),
            "account_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "Account No"}),
            "branch": forms.TextInput(attrs={"class": "form-control", "placeholder": "Branch"}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)


class FranchiseForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"}),
        required=True,
    )

    class Meta:
        model = Franchise
        fields = [
            "franchise_name",
            "franchise_owner",
            "franchise_place",
            "email",
            "mobile_no",
            "password",
            "confirm_password",
            "aadhar",
            "GST",
            "pan",
            "ac_no",
            "ifsc_code",
        ]
        widgets = {
            "ac_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "Account Number"}),
            "ifsc_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "IFSC Code"}),
        }

    def clean_ac_no(self):
        """ Validate Account Number (should be 9 to 18 digits). """
        ac_no = self.cleaned_data.get("ac_no")
        if not ac_no.isdigit() or not (9 <= len(ac_no) <= 18):
            raise ValidationError("Account Number must be between 9 to 18 digits and contain only numbers.")
        return ac_no

    def clean_ifsc_code(self):
        """ Validate IFSC Code (standard format: 4 letters, 0, 6 alphanumeric). """
        ifsc_code = self.cleaned_data.get("ifsc_code")
        if not ifsc_code or not RegexValidator(regex=r'^[A-Z]{4}0[A-Z0-9]{6}$')(ifsc_code):
            raise ValidationError("Enter a valid IFSC code (e.g., HDFC0001234).")
        return ifsc_code

    def clean(self):
        """ Ensure passwords match. """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")


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
        # Remove unwanted fields from the form
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
            # Apply the widgets as needed for each field
            "franchise": forms.Select(
                attrs={"class": "form-select form-control", "required": False}
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-user",
                    "placeholder": "First Name",
                }
            ),
            # Other fields' widgets as per your form...
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(LoanApplicationForm, self).__init__(*args, **kwargs)

        # Make franchise_referral not required if direct franchise selection is used
        self.fields["franchise"].required = False

        # Set queryset for assigned_to to show staff members, not admins
        self.fields["assigned_to"].queryset = StaffModel.objects.filter(
            is_active=True)

        # Disable fields as per user type or other conditions
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


class StaffAssignmentForm(forms.ModelForm):
    class Meta:
        model = StaffAssignmentModel
        fields = [
            "staff_name",
            "franchise_name",
            "franchise_mobile_no",
            "franchise_place",
            "assigned_by",  # Add this if needed in the form
            # If 'assign_to' is a necessary field, include it here as well
        ]
        widgets = {
            "staff_name": forms.Select(attrs={"class": "form-select form-control"}),
            "franchise_name": forms.Select(
                attrs={"class": "form-control form-control-user", "placeholder": "Select Franchise"}
            ),
            "franchise_mobile_no": forms.TextInput(
                attrs={"class": "form-control form-control-user", "placeholder": "Franchise Mobile No."}
            ),
            "franchise_place": forms.TextInput(
                attrs={"class": "form-control form-control-user", "placeholder": "Franchise Place"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(StaffAssignmentForm, self).__init__(*args, **kwargs)

        # Set the assigned_by field based on who is creating the assignment
        if user and isinstance(user, StaffModel):
            self.instance.assigned_by = user

        # If 'assign_to' field exists, set the queryset for it
        if 'assign_to' in self.fields:
            self.fields["assign_to"].queryset = StaffModel.objects.filter(is_active=True)

        # Dynamically update the franchise fields
        if self.instance.franchise_name:
            self.fields['franchise_mobile_no'].initial = self.instance.franchise_name.mobile_no
            self.fields['franchise_place'].initial = self.instance.franchise_name.place

        # Disable the fields initially until franchise is selected
        self.fields['franchise_mobile_no'].widget.attrs['disabled'] = 'disabled'
        self.fields['franchise_place'].widget.attrs['disabled'] = 'disabled'


    def clean_franchise_mobile_no(self):
        mobile = self.cleaned_data.get("franchise_mobile_no")
        if mobile and (len(mobile) != 10 or not mobile.isdigit()):
            raise ValidationError(
                "Franchise Mobile Number must be exactly 10 digits and contain only numbers."
            )
        return mobile


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
