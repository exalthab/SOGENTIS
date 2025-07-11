# accounts_users/profile_update_service.py 
from accounts_users.models.users_profile import UserProfile

def update_user_profile(user, data, files=None):
    profile = user.userprofile
    profile.full_name = data.get('full_name', profile.full_name)
    profile.phone = data.get('phone', profile.phone)
    profile.country = data.get('country', profile.country)
    profile.message = data.get('message', profile.message)
    profile.membership_role_id = data.get('membership_role') or profile.membership_role_id

    if files:
        if 'profile_picture' in files:
            profile.profile_picture = files['profile_picture']
        if 'judicial_record' in files:
            profile.judicial_record = files['judicial_record']

    profile.save()
    return profile






## accounts_users/profile_update_service.py -> 01/07
# def update_user_profile(profile, cleaned_data):
#     profile.full_name = cleaned_data.get('full_name')
#     profile.phone = cleaned_data.get('phone')
#     profile.country = cleaned_data.get('country')
#     profile.message = cleaned_data.get('message')
#     profile.judicial_record = cleaned_data.get('judicial_record')
#     profile.role = cleaned_data.get('role')
#     profile.save()
#     return profile
