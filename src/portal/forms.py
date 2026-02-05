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
        fields = ('user', 'customer', 'role')
    
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
        
        # If editing existing membership, hide customers field and use regular customer field
        if self.instance and self.instance.pk:
            # Editing: hide multi-select, show regular customer field
            if 'customers' in self.fields:
                del self.fields['customers']
            self.fields['customer'].queryset = available_customers
        else:
            # Adding: hide single customer field, show multi-select
            if 'customer' in self.fields:
                del self.fields['customer']
            self.fields['customers'].queryset = available_customers
            self.fields['customers'].required = True
    
    def save(self, commit=True):
        """Save CustomerMembership(s) for selected customers."""
        # If editing (has instance.pk), use normal save
        if self.instance and self.instance.pk:
            return super().save(commit=commit)
        
        # If adding new, handle multi-select
        customers = self.cleaned_data.get('customers', [])
        if not customers:
            # Shouldn't happen since field is required, but fallback
            return super().save(commit=commit)
        
        user = self.cleaned_data['user']
        role = self.cleaned_data['role']
        
        # Create/update memberships for each selected customer
        created = []
        updated = []
        for customer in customers:
            membership, created_flag = CustomerMembership.objects.get_or_create(
                user=user,
                customer=customer,
                defaults={'role': role}
            )
            if not created_flag:
                # Update role if membership already exists
                membership.role = role
                membership.save()
                updated.append(membership)
            else:
                created.append(membership)
        
        # Return the first one for compatibility with admin
        if created:
            return created[0]
        elif updated:
            return updated[0]
        return None
