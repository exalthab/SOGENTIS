import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts_users.models.users_profile import UserProfile
from social.models import Donation, Engagement, Project
from sogentis_apps.dashboard.views.utils import get_dashboard_stats

User = get_user_model()

@pytest.mark.django_db
def test_get_dashboard_stats_counts():
    # Setup data
    user = User.objects.create_user(email="test@example.com", password="pass")
    profile = UserProfile.objects.create(user=user, phone="123456", country="Testland")
    
    profile.role.name = "Volontaire"
    profile.role.save()
    
    project = Project.objects.create(name="Projet A", is_active=True)

    Donation.objects.create(user=user, project=project, amount=1000)
    Engagement.objects.create(user=user, project=project, created_at=timezone.now())

    # Call utility
    data = get_dashboard_stats()

    # Check counts
    assert data["stats"]["total_members"] == 1
    assert data["stats"]["total_volunteers"] == 1
    assert data["stats"]["total_donations"] == 1000
    assert data["stats"]["total_projects"] == 1
    assert data["stats"]["engagements_count"] == 1
    assert data["stats"]["donors_count"] == 1

    # Check cards structure
    assert len(data["cards"]) == 6
    assert all(len(item) == 4 for item in data["cards"])

    # Check detailed stats
    assert len(data["detailed_stats"]["donations_by_project"]) == 1
    assert data["detailed_stats"]["donations_by_project"][0]["total"] == 1000
    assert len(data["detailed_stats"]["engagements_by_year"]) == 1
