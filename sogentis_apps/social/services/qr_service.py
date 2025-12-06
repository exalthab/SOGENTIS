# social/services/qr_service.py
import qrcode
from django.conf import settings
import os
from datetime import datetime

class QRCodeService:

    @staticmethod
    def generate(donation):
        """
        Génère un QR Code lié au don.
        Le fichier est stocké dans /media/donations/qr/
        """
        folder = os.path.join(settings.MEDIA_ROOT, "donations", "qr")
        os.makedirs(folder, exist_ok=True)

        url = f"https://sogentis.org/donation/verify/{donation.id}/"

        filename = f"qr_{donation.id}.png"
        filepath = os.path.join(folder, filename)

        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(url)
        qr.make()
        img = qr.make_image()
        img.save(filepath)

        return settings.MEDIA_URL + f"donations/qr/{filename}"
