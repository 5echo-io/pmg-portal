"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Admin forms for bulk operations
Path: src/portal/forms.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django import forms
from .models import Customer, CustomerMembership


class BulkCustomerMembershipForm(forms.Form):
    """Form for creating multiple CustomerMemberships at once."""
    user = forms.ModelChoiceField(
        queryset=None,
        required=True,
        help_text="Select the user to assign to customers"
    )
    customers = forms.ModelMultipleChoiceField(
        queryset=Customer.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select one or more customers to assign this user to"
    )
    role = forms.ChoiceField(
        choices=CustomerMembership.ROLE_CHOICES,
        initial=CustomerMembership.ROLE_MEMBER,
        help_text="Role to assign for all selected customers"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['user'].queryset = User.objects.all()

    def save(self):
        """Create CustomerMembership records for each selected customer."""
        user = self.cleaned_data['user']
        customers = self.cleaned_data['customers']
        role = self.cleaned_data['role']
        
        created = []
        skipped = []
        for customer in customers:
            membership, created_flag = CustomerMembership.objects.get_or_create(
                user=user,
                customer=customer,
                defaults={'role': role}
            )
            if created_flag:
                created.append(membership)
            else:
                # Update role if membership already exists
                membership.role = role
                membership.save()
                skipped.append(membership)
        
        return created, skipped
