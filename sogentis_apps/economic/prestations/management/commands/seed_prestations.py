# /economic/prestations/management/commands/seed_prestations.py
from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.translation import activate

from economic.prestations.models import (
    PrestationCategory,
    Prestation,
    PrestationFeature,
    PrestationPackage,
    PrestationPackageFeature,
)


def _set_translation(obj, lang: str, **fields) -> None:
    obj.set_current_language(lang)
    for k, v in fields.items():
        setattr(obj, k, v)
    obj.save()


class Command(BaseCommand):
    help = "Seed default Prestations & Packages (safe upsert)."

    @transaction.atomic
    def handle(self, *args, **options):
        activate("fr")
        self.stdout.write(self.style.WARNING("Seeding prestations/packages…"))

        now = timezone.now()

        # =========================================================
        # 1) CATEGORIES (ServiceCategory) — upsert via slug
        # =========================================================
        categories_def = [
            # key, slug, name, description, featured, order
            ("design", "design-communication", "Design & Communication Visuelle",
             "Identité, logos, chartes graphiques, supports print & digital.", True, 10),
            ("cloud", "cloud-infrastructure", "Hébergement, Cloud & Infrastructure",
             "VPS/Cloud, DNS, SSL, migration, sauvegardes, monitoring.", True, 20),
            ("dev", "developpement-web-logiciels", "Développement Web & Logiciels",
             "Sites vitrines, e-commerce, applications métiers, intégrations.", True, 30),
            ("automation", "automatisation-digitalisation", "Automatisation & Digitalisation",
             "Workflows, reporting, intégrations, no-code/low-code.", False, 40),
            ("managed", "maintenance-infogerance", "Maintenance IT & Infogérance",
             "Support, supervision, mises à jour, correctifs, optimisation.", False, 50),
            ("security", "securite-sauvegardes", "Sécurité & Sauvegardes",
             "Hardening, PRA, audits, sauvegardes locales & cloud.", True, 60),
        ]

        cat_map: dict[str, PrestationCategory] = {}
        for key, slug, name, desc, featured, order in categories_def:
            cat, _ = PrestationCategory.objects.get_or_create(
                slug=slug,
                defaults={"is_active": True, "is_featured": featured, "order": order},
            )

            # Update non-translation fields (safe)
            PrestationCategory.objects.filter(pk=cat.pk).update(
                is_active=True,
                is_featured=featured,
                order=order,
                updated_at=now,
            )

            # Translations FR
            _set_translation(
                cat,
                "fr",
                name=name,
                description=desc,
                seo_title=f"{name} — SOGENTIS",
                seo_description=(desc[:157] + "...") if len(desc) > 160 else desc,
            )

            cat_map[key] = cat
            self.stdout.write(self.style.SUCCESS(f"Category seeded: {slug}"))

        # =========================================================
        # 2) PRESTATIONS — upsert via slug
        # =========================================================
        prestations_def = [
            # slug, cat_key, type, icon, featured, order, title, short, bullets
            ("design-communication", "design", Prestation.PrestationType.DESIGN, "fa-solid fa-pen-nib", True, 10,
             "Design & Communication Visuelle",
             "Affiches, logos, chartes graphiques, supports print & digital.",
             [
                 "Logos professionnels & refonte",
                 "Flyers, brochures, affiches",
                 "Charte graphique complète",
                 "Bannières digitales & visuels réseaux sociaux",
                 "Impression noir & couleur (options)",
             ]),
            ("cloud-infrastructure", "cloud", Prestation.PrestationType.CLOUD, "fa-solid fa-cloud", True, 20,
             "Hébergement, Cloud & Infrastructure",
             "VPS/Cloud, DNS, SSL, migration, sauvegardes, monitoring.",
             [
                 "Hébergement web (partagé/VPS/Cloud)",
                 "Gestion DNS & domaines",
                 "Certificats SSL & durcissement",
                 "Sauvegardes automatiques + restauration",
                 "Migration & optimisation performance/coûts",
             ]),
            ("developpement-web-logiciels", "dev", Prestation.PrestationType.DEV, "fa-solid fa-code", True, 30,
             "Développement Web & Logiciels",
             "Sites vitrines, e-commerce, applications métiers, ERP/CRM.",
             [
                 "Sites vitrines & e-commerce",
                 "Plateformes web & apps métiers",
                 "ERP/CRM personnalisés",
                 "Portails clients & intranets",
                 "Intégrations (paiement, SMS, email, API)",
             ]),
            ("automatisation-digitalisation", "automation", Prestation.PrestationType.AUTOMATION, "fa-solid fa-gears", False, 40,
             "Automatisation & Digitalisation",
             "Workflows, reporting, no-code/low-code, intégrations.",
             [
                 "Automatisation des tâches répétitives",
                 "Digitalisation des processus métier",
                 "Workflows intelligents",
                 "Tableaux de bord & KPI",
             ]),
            ("maintenance-infogerance", "managed", Prestation.PrestationType.MANAGED, "fa-solid fa-screwdriver-wrench", False, 50,
             "Maintenance IT & Infogérance",
             "Support, supervision, mises à jour, correctifs, optimisation.",
             [
                 "Maintenance préventive & corrective",
                 "Support à distance / sur site (option)",
                 "Supervision systèmes",
                 "Mises à jour & correctifs",
             ]),
            ("securite-sauvegardes", "security", Prestation.PrestationType.SECURITY, "fa-solid fa-shield-halved", True, 60,
             "Sécurité & Sauvegardes",
             "Hardening, PRA, audits, sauvegardes locales & cloud.",
             [
                 "Sécurité réseau & systèmes",
                 "Protection contre attaques courantes",
                 "Sauvegardes locales & cloud",
                 "PRA & procédures de restauration",
                 "Audit & recommandations",
             ]),
        ]

        prestation_map: dict[str, Prestation] = {}
        for slug, cat_key, ptype, icon, featured, order, title, short, bullets in prestations_def:
            p, _ = Prestation.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": cat_map.get(cat_key),
                    "prestation_type": ptype,
                    "deliverable": Prestation.Deliverable.OTHER,
                    "base_price": Decimal("0.00"),
                    "turnaround_days": 3,
                    "icon": icon,
                    "order": order,
                    "is_active": True,
                    "is_featured": featured,
                    "published_at": now,
                },
            )

            # Update non-translation fields
            Prestation.objects.filter(pk=p.pk).update(
                category=cat_map.get(cat_key),
                prestation_type=ptype,
                icon=icon,
                order=order,
                is_active=True,
                is_featured=featured,
                published_at=p.published_at or now,
                updated_at=now,
            )

            # Translations FR
            _set_translation(
                p,
                "fr",
                title=title,
                short_description=short,
                description=short,
                seo_title=f"{title} — SOGENTIS",
                seo_description=(short[:157] + "...") if len(short) > 160 else short,
            )

            # Features (reset simple)
            p.features.all().delete()
            for i, b in enumerate(bullets, start=1):
                PrestationFeature.objects.create(prestation=p, label=b, order=i * 10)

            prestation_map[slug] = p
            self.stdout.write(self.style.SUCCESS(f"Prestation seeded: {slug}"))

        # =========================================================
        # 3) PACKS — upsert via slug (ou name), M2M "prestations" (ou fallback "services")
        # =========================================================
        packages_def = [
            # slug, tier, price, currency, period, support, featured, order, included_domain, included_ssl, emails, max_pages, name, tagline, feats, prestation_slugs
            ("starter", PrestationPackage.Tier.STARTER, Decimal("99.00"), PrestationPackage.Currency.EUR,
             PrestationPackage.BillingPeriod.YEARLY, PrestationPackage.SupportLevel.STANDARD, False, 10,
             True, True, 1, 3,
             "Pack STARTER", "Idéal pour débuter",
             [
                 ("Nom de domaine offert (1 an)", True),
                 ("Certificat SSL inclus", True),
                 ("1 e-mail professionnel", False),
                 ("Site basique (1–3 pages)", False),
                 ("Support standard", False),
             ],
             ["design-communication", "cloud-infrastructure"]),
            ("business", PrestationPackage.Tier.BUSINESS, Decimal("299.00"), PrestationPackage.Currency.EUR,
             PrestationPackage.BillingPeriod.YEARLY, PrestationPackage.SupportLevel.PRIORITY, True, 20,
             True, True, 5, 10,
             "Pack BUSINESS", "Pour PME & Entrepreneurs",
             [
                 ("Nom de domaine offert (1 an)", True),
                 ("SEO de base", True),
                 ("5 e-mails professionnels (1 an)", False),
                 ("Site jusqu’à 10 pages", False),
                 ("Sauvegardes automatiques", True),
                 ("Support prioritaire", True),
             ],
             ["developpement-web-logiciels", "cloud-infrastructure", "securite-sauvegardes"]),
            ("premium", PrestationPackage.Tier.PREMIUM, Decimal("699.00"), PrestationPackage.Currency.EUR,
             PrestationPackage.BillingPeriod.YEARLY, PrestationPackage.SupportLevel.DEDICATED, True, 30,
             True, True, 10, None,
             "Pack PREMIUM", "Solution complète",
             [
                 ("Nom de domaine offert (1 an)", True),
                 ("Hébergement VPS/Cloud", True),
                 ("SSL avancé + durcissement HTTPS", True),
                 ("SEO avancé", True),
                 ("10 e-mails professionnels", False),
                 ("Sauvegardes quotidiennes", True),
                 ("Maintenance & support inclus", True),
             ],
             ["developpement-web-logiciels", "cloud-infrastructure", "securite-sauvegardes", "maintenance-infogerance"]),
            ("sur-mesure", PrestationPackage.Tier.CUSTOM, Decimal("0.00"), PrestationPackage.Currency.EUR,
             PrestationPackage.BillingPeriod.CUSTOM, PrestationPackage.SupportLevel.DEDICATED, False, 999,
             False, True, 0, None,
             "Pack SUR MESURE", "Sur devis",
             [
                 ("ERP / CRM personnalisé", True),
                 ("Plateforme web ou application", True),
                 ("Automatisation avancée", True),
                 ("Infrastructure Cloud dédiée", True),
                 ("Infogérance complète", True),
                 ("Sécurité & conformité", True),
             ],
             ["developpement-web-logiciels", "automatisation-digitalisation", "cloud-infrastructure", "securite-sauvegardes"]),
        ]

        # M2M field name compatibility: "prestations" (nouveau) ou "services" (ancien)
        m2m_name = "prestations" if hasattr(PrestationPackage, "prestations") else "services"

        for (
            slug, tier, price, currency, period, support, featured, order,
            inc_domain, inc_ssl, emails, max_pages,
            name, tagline, feats, prestation_slugs
        ) in packages_def:
            pack, _ = PrestationPackage.objects.get_or_create(
                slug=slug,
                defaults={
                    "tier": tier,
                    "billing_period": period,
                    "support_level": support,
                    "total_price": price,
                    "currency": currency,
                    "included_domain_year": inc_domain,
                    "included_ssl": inc_ssl,
                    "emails_count": emails,
                    "max_pages": max_pages,
                    "order": order,
                    "is_featured": featured,
                    "is_active": True,
                    "published_at": now,
                },
            )

            # Update non-translation fields
            PrestationPackage.objects.filter(pk=pack.pk).update(
                tier=tier,
                billing_period=period,
                support_level=support,
                total_price=price,
                currency=currency,
                included_domain_year=inc_domain,
                included_ssl=inc_ssl,
                emails_count=emails,
                max_pages=max_pages,
                order=order,
                is_featured=featured,
                is_active=True,
                published_at=pack.published_at or now,
                updated_at=now,
            )

            # Translations FR
            _set_translation(
                pack,
                "fr",
                name=name,
                tagline=tagline,
                cta_label="Demander un devis",
                seo_title=f"{name} — SOGENTIS",
                seo_description=(tagline[:157] + "...") if len(tagline) > 160 else tagline,
                description=tagline,
            )

            # Features reset
            pack.features.all().delete()
            for i, (lbl, hi) in enumerate(feats, start=1):
                PrestationPackageFeature.objects.create(
                    package=pack,
                    label=lbl,
                    is_highlight=bool(hi),
                    order=i * 10,
                )

            # M2M set
            rel = getattr(pack, m2m_name)
            rel.clear()
            for pslug in prestation_slugs:
                pobj = prestation_map.get(pslug)
                if pobj:
                    rel.add(pobj)

            self.stdout.write(self.style.SUCCESS(f"Package seeded: {slug}"))

        self.stdout.write(self.style.SUCCESS("✅ Seed completed."))






# # /economic/prestations/management/commands/seed_prestations.py
# from __future__ import annotations

# from django.core.management.base import BaseCommand
# from django.utils.timezone import now
# from django.utils.translation import activate
 
# from economic.prestations.models import (
#     Service, ServiceFeature, ServiceCategory,
#     Package, PackageFeature, PackageTier, BillingPeriod, Currency, SupportLevel,
# )


# class Command(BaseCommand):
#     help = "Seed default Services & Packages (safe upsert)."

#     def handle(self, *args, **options):
#         # On seed en FR par défaut (tu peux dupliquer en EN si besoin)
#         activate("fr")

#         self.stdout.write(self.style.WARNING("Seeding services/packages…"))

#         services_def = [
#             ("design_com", ServiceCategory.DESIGN, "fa-solid fa-pen-nib", True, 10,
#              "Design & Communication Visuelle",
#              "Affiches, logos, chartes graphiques, supports print & digital.",
#              [
#                  "Logos professionnels & refonte",
#                  "Flyers, brochures, affiches",
#                  "Charte graphique complète",
#                  "Bannières digitales & visuels réseaux sociaux",
#                  "Impression noir & couleur (options)",
#              ]),
#             ("cloud_infra", ServiceCategory.CLOUD, "fa-solid fa-cloud", True, 20,
#              "Hébergement, Cloud & Infrastructure",
#              "VPS/Cloud, DNS, SSL, migration, sauvegardes, monitoring.",
#              [
#                  "Hébergement web (partagé/VPS/Cloud)",
#                  "Gestion DNS & domaines",
#                  "Certificats SSL & durcissement",
#                  "Sauvegardes automatiques + restauration",
#                  "Migration & optimisation performance/coûts",
#              ]),
#             ("web_dev", ServiceCategory.DEV, "fa-solid fa-code", True, 30,
#              "Développement Web & Logiciels",
#              "Sites vitrines, e-commerce, applications métiers, ERP/CRM.",
#              [
#                  "Sites vitrines & e-commerce",
#                  "Plateformes web & apps métiers",
#                  "ERP/CRM personnalisés",
#                  "Portails clients & intranets",
#                  "Intégrations (paiement, SMS, email, API)",
#              ]),
#             ("automation", ServiceCategory.AUTOMATION, "fa-solid fa-gears", False, 40,
#              "Automatisation & Digitalisation",
#              "Workflows, reporting, no-code/low-code, intégrations.",
#              [
#                  "Automatisation des tâches répétitives",
#                  "Digitalisation des processus métier",
#                  "Workflows intelligents",
#                  "Tableaux de bord & KPI",
#              ]),
#             ("managed_it", ServiceCategory.MANAGED, "fa-solid fa-screwdriver-wrench", False, 50,
#              "Maintenance IT & Infogérance",
#              "Support, supervision, mises à jour, correctifs, optimisation.",
#              [
#                  "Maintenance préventive & corrective",
#                  "Support à distance / sur site (option)",
#                  "Supervision systèmes",
#                  "Mises à jour & correctifs",
#              ]),
#             ("security_backup", ServiceCategory.SECURITY, "fa-solid fa-shield-halved", True, 60,
#              "Sécurité & Sauvegardes",
#              "Hardening, PRA, audits, sauvegardes locales & cloud.",
#              [
#                  "Sécurité réseau & systèmes",
#                  "Protection contre attaques courantes",
#                  "Sauvegardes locales & cloud",
#                  "PRA & procédures de restauration",
#                  "Audit & recommandations",
#              ]),
#         ]

#         service_objs = {}
#         for code, cat, icon, featured, order, name, short, bullets in services_def:
#             service, created = Service.objects.get_or_create(
#                 code=code,
#                 defaults={
#                     "category": cat,
#                     "icon": icon,
#                     "is_featured": featured,
#                     "order": order,
#                     "is_published": True,
#                     "published_at": now(),
#                 },
#             )

#             # Update non-translation fields
#             Service.objects.filter(pk=service.pk).update(
#                 category=cat, icon=icon, is_featured=featured, order=order, is_published=True
#             )

#             # Translations
#             service.set_current_language("fr")
#             service.name = name
#             service.slug = code.replace("_", "-")
#             service.short_description = short
#             if not service.published_at:
#                 service.published_at = now()
#             service.save()

#             # Features upsert (simple: reset)
#             service.features.all().delete()
#             for i, b in enumerate(bullets, start=1):
#                 ServiceFeature.objects.create(service=service, label=b, order=i * 10)

#             service_objs[code] = service

#             self.stdout.write(self.style.SUCCESS(f"Service seeded: {code}"))

#         # Packages
#         packages_def = [
#             ("starter", PackageTier.STARTER, 99, Currency.EUR, BillingPeriod.YEARLY, SupportLevel.STANDARD, True, 1, 3, 10,
#              "Pack STARTER", "Idéal pour débuter",
#              [
#                  ("Nom de domaine offert (1 an)", True),
#                  ("Hébergement web (1 an)", False),
#                  ("Certificat SSL inclus", True),
#                  ("1 e-mail professionnel", False),
#                  ("Site basique (1–3 pages)", False),
#                  ("Support standard", False),
#              ],
#              ["design_com", "cloud_infra"]),
#             ("business", PackageTier.BUSINESS, 299, Currency.EUR, BillingPeriod.YEARLY, SupportLevel.PRIORITY, True, 5, 10, 20,
#              "Pack BUSINESS", "Pour PME & Entrepreneurs",
#              [
#                  ("Nom de domaine offert (1 an)", True),
#                  ("Hébergement performant (1 an)", False),
#                  ("SEO de base", True),
#                  ("5 e-mails professionnels (1 an)", False),
#                  ("Site jusqu’à 10 pages", False),
#                  ("Sauvegardes automatiques", True),
#                  ("Support prioritaire", True),
#              ],
#              ["web_dev", "cloud_infra", "security_backup"]),
#             ("premium", PackageTier.PREMIUM, 699, Currency.EUR, BillingPeriod.YEARLY, SupportLevel.DEDICATED, True, 10, None, 5,
#              "Pack PREMIUM", "Solution complète",
#              [
#                  ("Nom de domaine offert (1 an)", True),
#                  ("Hébergement VPS/Cloud", True),
#                  ("SSL avancé + durcissement HTTPS", True),
#                  ("SEO avancé", True),
#                  ("10 e-mails professionnels", False),
#                  ("Site complet ou e-commerce (selon périmètre)", False),
#                  ("Sauvegardes quotidiennes", True),
#                  ("Maintenance & support inclus", True),
#              ],
#              ["web_dev", "cloud_infra", "security_backup", "managed_it"]),
#             ("sur-mesure", PackageTier.CUSTOM, 0, Currency.EUR, BillingPeriod.CUSTOM, SupportLevel.DEDICATED, False, 0, None, 999,
#              "Pack SUR MESURE", "Sur devis",
#              [
#                  ("ERP / CRM personnalisé", True),
#                  ("Plateforme web ou application", True),
#                  ("Automatisation avancée", True),
#                  ("Infrastructure Cloud dédiée", True),
#                  ("Infogérance complète", True),
#                  ("Sécurité & conformité", True),
#              ],
#              ["web_dev", "automation", "cloud_infra", "security_backup"]),
#         ]

#         for code, tier, price, currency, period, support, ssl, emails, max_pages, order, name, tagline, feats, service_codes in packages_def:
#             pack, _ = Package.objects.get_or_create(
#                 code=code,
#                 defaults={
#                     "tier": tier,
#                     "price_amount": price,
#                     "price_currency": currency,
#                     "billing_period": period,
#                     "support_level": support,
#                     "included_ssl": ssl,
#                     "emails_count": emails,
#                     "max_pages": max_pages,
#                     "order": order,
#                     "is_featured": tier in (PackageTier.BUSINESS, PackageTier.PREMIUM),
#                     "is_published": True,
#                 },
#             )

#             Package.objects.filter(pk=pack.pk).update(
#                 tier=tier,
#                 price_amount=price,
#                 price_currency=currency,
#                 billing_period=period,
#                 support_level=support,
#                 included_ssl=ssl,
#                 emails_count=emails,
#                 max_pages=max_pages,
#                 order=order,
#                 is_published=True,
#             )

#             pack.set_current_language("fr")
#             pack.name = name
#             pack.slug = code
#             pack.tagline = tagline
#             pack.cta_label = "Demander un devis"
#             pack.save()

#             pack.features.all().delete()
#             for i, (lbl, hi) in enumerate(feats, start=1):
#                 PackageFeature.objects.create(package=pack, label=lbl, is_highlight=hi, order=i * 10)

#             pack.included_services.clear()
#             for sc in service_codes:
#                 if sc in service_objs:
#                     pack.included_services.add(service_objs[sc])

#             self.stdout.write(self.style.SUCCESS(f"Package seeded: {code}"))

#         self.stdout.write(self.style.SUCCESS("✅ Seed completed."))
