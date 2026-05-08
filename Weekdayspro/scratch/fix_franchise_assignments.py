import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'properties.settings')
django.setup()

from prop.models import AddPropertyModel, FranchiseProperty, User

def assign_existing_properties():
    # Get all unverified properties added by Owners that don't have a FranchiseProperty entry
    properties = AddPropertyModel.objects.filter(
        is_verified=False,
        user__role='OWNER'
    ).exclude(franchiseproperty__isnull=False)

    print(f"Found {properties.count()} unassigned properties.")

    # Get all users with FRANCHISE role
    franchises = User.objects.filter(role='FRANCHISE').exclude(location__isnull=True).exclude(location='')

    assigned_count = 0
    for prop in properties:
        address_str = prop.address.lower() if prop.address else ""
        assigned_franchise = None
        
        for fran in franchises:
            fran_loc = fran.location.lower() if fran.location else ""
            if fran_loc and address_str and (fran_loc in address_str or address_str in fran_loc):
                assigned_franchise = fran
                break
        
        if assigned_franchise:
            FranchiseProperty.objects.get_or_create(
                property=prop,
                franchise=assigned_franchise,
                defaults={'property_id_number': prop.id}
            )
            print(f"Assigned Property ID {prop.id} to Franchise {assigned_franchise.username}")
            assigned_count += 1
    
    print(f"Total assigned: {assigned_count}")

if __name__ == "__main__":
    assign_existing_properties()
