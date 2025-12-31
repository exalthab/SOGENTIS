from django.shortcuts import render

from economic.support.services import get_active_faqs


def faq_list_view(request):
    faqs = get_active_faqs()
    return render(request, "economic/support/faq/faq_list.html", {"faqs": faqs})
