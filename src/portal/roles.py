"""
Role hierarchy and permission helpers for PMG Portal.

Hierarchy (highest first):
- Platform admin (is_superuser): see/manage all tenants, override all roles, create/delete tenants.
  Invisible to users below this level. Cannot delete self.
- Super admin: almost same as platform admin, cannot change/delete platform admins. Cannot delete self.
- Owner (per tenant): owns the tenant; only owner can change/delete owner; can transfer ownership.
- Administrator (per tenant): most rights except system settings; cannot delete users with higher role.
- User (per tenant): regular portal user.

Rule: A user cannot delete or assign a role above their own level.
"""
from django.contrib.auth import get_user_model

User = get_user_model()

# Hierarchy levels (higher = more privileged). Used for comparison only.
LEVEL_PLATFORM_ADMIN = 50
LEVEL_SUPER_ADMIN = 40
LEVEL_OWNER = 30
LEVEL_ADMINISTRATOR = 20
LEVEL_USER = 10

# Tenant (customer) role names - default roles that cannot be deleted as types
ROLE_OWNER = "owner"
ROLE_ADMINISTRATOR = "administrator"
ROLE_USER = "user"

# Legacy aliases (member -> user, admin -> administrator) for backward compat in level lookup
TENANT_ROLE_LEVELS = {
    ROLE_OWNER: LEVEL_OWNER,
    ROLE_ADMINISTRATOR: LEVEL_ADMINISTRATOR,
    ROLE_USER: LEVEL_USER,
    "admin": LEVEL_ADMINISTRATOR,  # legacy
    "member": LEVEL_USER,  # legacy
}


def get_system_role(user):
    """
    Return system-level role: 'platform_admin', 'super_admin', or None.
    Platform admin = is_superuser. Super admin = UserProfile.system_role == 'super_admin'.
    """
    if not user or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False):
        return "platform_admin"
    profile = getattr(user, "portal_profile", None)
    if profile and getattr(profile, "system_role", None) == "super_admin":
        return "super_admin"
    return None


def get_system_role_level(user):
    """Return hierarchy level for system role only (or 0 if none)."""
    role = get_system_role(user)
    if role == "platform_admin":
        return LEVEL_PLATFORM_ADMIN
    if role == "super_admin":
        return LEVEL_SUPER_ADMIN
    return 0


def get_tenant_role_level(role_name):
    """Return hierarchy level for a tenant role name."""
    return TENANT_ROLE_LEVELS.get(role_name, LEVEL_USER)


def get_effective_level(user, customer=None):
    """
    Effective hierarchy level for user: max of system role and tenant role (for given customer).
    If customer is None, returns system role level if any, else 0 (no tenant context).
    """
    level = get_system_role_level(user)
    if customer and hasattr(user, "customer_memberships"):
        from portal.models import CustomerMembership
        membership = CustomerMembership.objects.filter(user=user, customer=customer).first()
        if membership:
            level = max(level, get_tenant_role_level(membership.role))
    elif customer:
        from portal.models import CustomerMembership
        membership = CustomerMembership.objects.filter(user=user, customer=customer).first()
        if membership:
            level = max(level, get_tenant_role_level(membership.role))
    return level


def is_platform_admin(user):
    return get_system_role(user) == "platform_admin"


def is_super_admin(user):
    return get_system_role(user) == "super_admin"


def is_owner(user, customer):
    """True if user is owner for this customer (tenant)."""
    from portal.models import CustomerMembership
    return CustomerMembership.objects.filter(
        user=user, customer=customer, role=ROLE_OWNER
    ).exists()


def can_see_user(actor, target):
    """
    Whether actor is allowed to see target in user lists/details.
    Platform admins are invisible to non-platform-admins.
    """
    if not actor or not actor.is_authenticated or not target:
        return False
    if actor.pk == target.pk:
        return True
    actor_sys = get_system_role(actor)
    target_sys = get_system_role(target)
    # Only platform admins can see platform admins
    if target_sys == "platform_admin":
        return actor_sys == "platform_admin"
    return True


def can_manage_user(actor, target, customer=None):
    """
    Whether actor can edit or delete target (and change their role).
    - Cannot manage self for delete (and optionally for role demotion).
    - Platform admin can manage everyone except cannot delete self.
    - Super admin can manage everyone except platform admins; cannot delete self.
    - Owner can manage users in same tenant up to administrator; cannot delete self; only owner can change/delete owner.
    - Administrator can manage users in same tenant up to user level only.
    - User cannot manage anyone.
    """
    if not actor or not actor.is_authenticated or not target:
        return False
    if actor.pk == target.pk:
        # Self: edit allowed (e.g. profile), delete never
        return "edit_only"  # caller can treat as "can_edit but not delete"

    actor_level = get_effective_level(actor, customer)
    target_sys = get_system_role(target)

    # Only platform admin can manage platform admins
    if target_sys == "platform_admin":
        return get_system_role(actor) == "platform_admin"

    target_level = get_system_role_level(target)
    if target_level == 0 and customer:
        from portal.models import CustomerMembership
        m = CustomerMembership.objects.filter(user=target, customer=customer).first()
        target_level = get_tenant_role_level(m.role) if m else LEVEL_USER

    # Super admin cannot manage platform admin (already handled above)
    # Actor must have strictly higher level to manage target (or equal for same-role restrictions)
    if actor_level <= target_level:
        return False
    return True


def can_edit_user(actor, target, customer=None):
    """Whether actor can edit target (including role). Self is allowed for own profile."""
    if not actor or not actor.is_authenticated or not target:
        return False
    if actor.pk == target.pk:
        return True
    return can_manage_user(actor, target, customer) is True


def can_delete_user(actor, target, customer=None):
    """Whether actor can delete target. Never allowed for self."""
    if actor and target and actor.pk == target.pk:
        return False
    return can_manage_user(actor, target, customer) is True


def get_assignable_tenant_roles(actor, customer=None):
    """
    Return list of (value, label) for tenant roles that actor can assign.
    Actor can only assign roles at or below their own level.
    """
    from portal.models import CustomerMembership

    level = get_effective_level(actor, customer)
    choices = []
    if level >= LEVEL_OWNER:
        choices.append((ROLE_OWNER, "Owner"))
    if level >= LEVEL_ADMINISTRATOR:
        choices.append((ROLE_ADMINISTRATOR, "Administrator"))
    if level >= LEVEL_USER:
        choices.append((ROLE_USER, "User"))
    return choices


def get_assignable_tenant_roles_for_form(actor, customer=None):
    """Same as get_assignable_tenant_roles; use in forms. Includes legacy member/admin if needed for display."""
    return get_assignable_tenant_roles(actor, customer)


def can_access_system_settings(user):
    """Only platform admin can change global/system settings."""
    return get_system_role(user) == "platform_admin"


def can_create_delete_tenants(user):
    """Only platform admin can create/delete tenants (customers)."""
    return get_system_role(user) == "platform_admin"


def can_edit_owner_membership(actor, membership, customer=None):
    """Only owner (or above) can change/remove owner membership; and only owner can assign owner."""
    from portal.models import CustomerMembership
    if membership.role != ROLE_OWNER:
        return can_manage_user(actor, membership.user, customer)
    # Changing an owner record: only same-tenant owner or system roles above owner
    actor_level = get_effective_level(actor, customer or membership.customer)
    if actor_level < LEVEL_OWNER:
        return False
    if actor.pk == membership.user_id:
        return True  # owner can change own membership (e.g. transfer)
    return can_manage_user(actor, membership.user, customer or membership.customer)


def compute_is_staff(user):
    """
    True if user should have staff access: Platform admin, Super admin, or any tenant role
    Administrator or higher (Owner, Administrator). Used to derive is_staff; not shown in UI.
    """
    if not user or not user.pk:
        return False
    if getattr(user, "is_superuser", False):
        return True
    profile = getattr(user, "portal_profile", None)
    if profile is not None and getattr(profile, "system_role", None) == "super_admin":
        return True
    from portal.models import CustomerMembership
    return CustomerMembership.objects.filter(
        user_id=user.pk,
        role__in=[ROLE_OWNER, ROLE_ADMINISTRATOR],
    ).exists()


def sync_user_is_staff(user):
    """Set user.is_staff from role hierarchy and save. Call after membership or user role changes."""
    if not user or not user.pk:
        return
    new_value = compute_is_staff(user)
    if user.is_staff != new_value:
        user.is_staff = new_value
        user.save(update_fields=["is_staff"])
