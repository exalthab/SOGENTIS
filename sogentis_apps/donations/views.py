# donations/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from donations.models import Donation

@login_required
def donation_create_view(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        project_id = request.POST.get("project")

        donation = Donation.objects.create(
            user=request.user,
            project_id=project_id or None,
            amount=amount,
            status=Donation.STATUS_PENDING,
        )
        request.session["donation_id"] = donation.id
        return redirect("donations:payment_choice")

    return render(request, "donations/donation_form.html")





# from django.shortcuts import render
# from django.http import HttpResponse

# def create(request):
#     return HttpResponse("Page de création de don 💖")
