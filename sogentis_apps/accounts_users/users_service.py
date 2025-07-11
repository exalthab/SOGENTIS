# accounts_users/users_service.py
from django.contrib.auth import get_user_model
from accounts_users.models.users_profile import UserProfile

User = get_user_model()

def create_user_with_profile(user_data, profile_data, files=None):
    user = User.objects.create_user(
        email=user_data['email'],
        username=user_data['username'],
        password=user_data['password'],
        is_active=False  # Activation requise par e-mail
    )

    profile = UserProfile.objects.create(
        user=user,
        full_name=profile_data.get('full_name'),
        phone=profile_data.get('phone'),
        country=profile_data.get('country'),
        message=profile_data.get('message'),
        membership_role_id=profile_data.get('membership_role'),
        profile_picture=files.get('profile_picture') if files else None,
        judicial_record=files.get('judicial_record') if files else None,
    )

    return user

def generate_membership_code(role_code):
    prefix = {
        'MEMBER': 'M',
        'SPONSOR': 'D',
        'VOLUNTEER': 'V',
        'INSTITUTION': 'I'
    }.get(role_code, 'X')

    last_profile = UserProfile.objects.filter(
        membership_role__code=role_code,
        membership_code__startswith=prefix
    ).order_by('-membership_code').first()

    if last_profile and last_profile.membership_code:
        last_number = int(last_profile.membership_code[1:])
    else:
        last_number = 0

    return f"{prefix}{last_number + 1:03d}"




## accounts_users/users_service.py
# from accounts_users.models.users import CustomUser

# def get_active_users():
#     return CustomUser.objects.filter(is_active=True)

# def create_user_with_profile(user_data, profile_data):
#     user = CustomUser.objects.create_user(email=user_data['email'], password=user_data['password'])
#     user.userprofile.full_name = profile_data['full_name']
#     user.userprofile.phone = profile_data['phone']
#     user.userprofile.country = profile_data['country']
#     user.userprofile.save()
#     return user
