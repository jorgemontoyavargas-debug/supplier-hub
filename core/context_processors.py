from organizations.models import Membership


def navigation_permissions(request):
    if not request.user.is_authenticated:
        return {}
    memberships = request.user.memberships.filter(is_active=True)
    return {
        "has_buyer_access": memberships.exists(),
        "has_review_access": memberships.filter(
            role__in=(
                Membership.Role.ADMIN,
                Membership.Role.REVIEWER,
                Membership.Role.APPROVER,
            )
        ).exists(),
        "has_integration_access": memberships.filter(
            role__in=(Membership.Role.ADMIN, Membership.Role.CATEGORY_MANAGER)
        ).exists(),
        "has_supplier_access": request.user.supplier_contacts.exists(),
    }
