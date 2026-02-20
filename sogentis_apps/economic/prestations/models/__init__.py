# economic/prestations/models/__init__.py
from .prestations_category import PrestationCategory  # noqa
from .prestations import Prestation, PrestationFeature  # noqa
from .prestations_package import PrestationPackage, PrestationPackageFeature  # noqa
from .prestations_request import PrestationRequest  # noqa
from .prestations_quote import Quote, QuoteLine  # noqa

# Infomaniak-like options / paiement / livrables / appels d'offres
from .offers import PrestationPlan, PackageOffer  # noqa
from .entitlements import PrestationEntitlement  # noqa
from .projects import ProjectCall, ProjectAttachment, ProjectBid  # noqa

__all__ = [
    "PrestationCategory",
    "Prestation",
    "PrestationFeature",
    "PrestationPackage",
    "PrestationPackageFeature",
    "PrestationRequest",
    "Quote",
    "QuoteLine",
    "PrestationPlan",
    "PackageOffer",
    "PrestationEntitlement",
    "ProjectCall",
    "ProjectAttachment",
    "ProjectBid",
]







# # economic/prestations/models/__init__.py
# from .prestations_category import PrestationCategory  # noqa
# from .prestations import Prestation, PrestationFeature  # noqa
# from .prestations_package import PrestationPackage, PrestationPackageFeature  # noqa
# from .prestations_request import PrestationRequest  # noqa
# from .prestations_quote import Quote, QuoteLine  # noqa

# __all__ = [
#     "PrestationCategory",
#     "Prestation",
#     "PrestationFeature",
#     "PrestationPackage",
#     "PrestationPackageFeature",
#     "PrestationRequest",
#     "Quote",
#     "QuoteLine",
# ]






# # economic/prestations/models/__init__.py
# from .prestations_category import ServiceCategory  # noqa
# from .prestations import Service, ServiceFeature  # noqa
# from .prestations_package import ServicePackage, ServicePackageFeature  # noqa
# from .prestations_request import ServiceRequest  # noqa
# from .prestations_quote import Quote, QuoteLine  # noqa

# __all__ = [
#     "ServiceCategory",
#     "Service",
#     "ServiceFeature",
#     "ServicePackage",
#     "ServicePackageFeature",
#     "ServiceRequest",
#     "Quote",
#     "QuoteLine",
# ]





# # economic/services/models/__init__.py

# from .service_category import ServiceCategory  # noqa
# from .service import Service, ServiceFeature  # noqa
# from .service_package import ServicePackage, ServicePackageFeature  # noqa
# from .service_request import ServiceRequest  # noqa
# from .quote import Quote, QuoteLine  # noqa

# __all__ = [
#     "ServiceCategory",
#     "Service",
#     "ServiceFeature",
#     "ServicePackage",
#     "ServicePackageFeature",
#     "ServiceRequest",
#     "QuoteLine",
# ]






# # economic/services/models/__init__.py
# from .service_category import ServiceCategory  # noqa
# from .service import Service  # noqa
# from .service_package import ServicePackage  # noqa
# from .service_request import ServiceRequest  # noqa






# from .service_category import ServiceCategory
# from .service import Service
# from .service_package import ServicePackage
# from .service_request import ServiceRequest


# __all__ = [
#     "ServiceCategory",
#     "Service",
#     "ServicePackage",
#     "ServiceRequest",
# ]
