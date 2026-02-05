"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Admin forms for CustomerMembership
Path: src/portal/forms.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django import forms
from .models import Customer, CustomerMembership


class CustomerMembershipForm(forms.ModelForm):
    """Form for CustomerMembership with multi-select customer support for adding."""
    customers = forms.ModelMultipleChoiceField(
        queryset=Customer.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': '10', 'class': 'vSelectMultipleField'}),
        help_text="Select one or more customers (hold Ctrl/Cmd to select multiple). Only shown when adding new membership."
    )
    
    class Meta:
        model = CustomerMembership
        fields = ('user', 'role')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Get available customers based on user permissions
        if self.request:
            user = self.request.user
            if user.is_superuser:
                # PMG admins can see all customers
                available_customers = Customer.objects.all()
            else:
                # Customer admins can only see their own customer
                available_customers = Customer.objects.filter(
                    customermembership__user=user,
                    customermembership__role=CustomerMembership.ROLE_ADMIN
                )
        else:
            available_customers = Customer.objects.all()
        
        # If editing existing membership, add customer field and hide customers field
        if self.instance and self.instance.pk:
            # Editing: add customer field, hide multi-select
            if 'customers' in self.fields:
                del self.fields['customers']
            # Add customer field for editing
            self.fields['customer'] = forms.ModelChoiceField(
                queryset=available_customers,
                required=True,
                initial=self.instance.customer
            )
        else:
            # Adding: ensure customers field is present and required
            self.fields['customers'].queryset = available_customers
            self.fields['customers'].required = True
    
    def save(self, commit=True):
        """Save CustomerMembership(s) for selected customers."""
        # If editing (has instance.pk), use normal save
        if self.instance and self.instance.pk:
            return super().save(commit=commit)
        
        # If adding new, create a dummy instance (will be handled in save_model)
        # We need to return an instance for Django admin
        instance = super().save(commit=False)
        if commit:
            # Don't save here - save_model will handle it
            pass
        return instance
    
    def save_m2m(self):
        """Override save_m2m to prevent Django admin from trying to save M2M."""
        # We handle saving in save_model, so this is a no-op
        pass
