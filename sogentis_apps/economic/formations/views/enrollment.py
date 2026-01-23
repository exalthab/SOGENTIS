# economic/formations/views/enrollment.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _, get_language

from ..models import Course, Enrollment


@login_required
def enroll_view(request, slug):
    lang = get_language()
    course = get_object_or_404(Course.objects.language(lang), slug=slug, is_active=True)

    existing = Enrollment.objects.filter(user=request.user, course=course).exclude(
        status=Enrollment.Status.CANCELLED
    ).first()
    if existing:
        messages.info(request, _("Vous êtes déjà inscrit à cette formation."))
        return redirect("economic:formations:course_detail", slug=course.slug)

    # Gratuit => active + paid True
    is_free = course.is_free
    enrollment = Enrollment.objects.create(
        user=request.user,
        course=course,
        status=Enrollment.Status.ACTIVE if is_free else Enrollment.Status.PENDING,
        paid=True if is_free else False,
    )

    if is_free:
        messages.success(request, _("Inscription confirmée. Bonne formation !"))
    else:
        messages.success(request, _("Inscription enregistrée. Paiement requis (à brancher)."))

    return render(request, "economic/formations/courses/enroll_confirm.html", {
        "course": course,
        "enrollment": enrollment,
    })





# from django.shortcuts import redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils.translation import gettext as _

# from ..models.course import Course


# @login_required
# def enroll_view(request, slug):
#     """
#     Inscription à une formation.
#     Pour l'instant :
#     - vérifie que la formation existe
#     - affiche un message de succès
#     - redirige vers la vue d'apprentissage (learning)
#     Tu pourras brancher ici un vrai modèle d'inscription plus tard.
#     """
#     course = get_object_or_404(Course, slug=slug)

#     if request.method == "POST":
#         # TODO : créer un objet d'inscription réel (CourseEnrollment, etc.)
#         messages.success(
#             request,
#             _("Votre inscription à la formation « %(title)s » est bien prise en compte.") % {
#                 "title": course.title if hasattr(course, "title") else course
#             },
#         )
#         return redirect("economic:formations:learning", slug=course.slug)

#     # Si ce n’est pas un POST, on renvoie vers la page détail
#     return redirect("economic:formations:course_detail", slug=course.slug)
