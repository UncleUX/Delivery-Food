from django.conf import settings
from restaurantCommande.models.commande import Commande
from notifications.notifications_message import notifications_message
from core.tenant import set_tenant_from_restaurant
import time


def notif_cancel_commande(request, commande, client, restaurant):
    """DocString."""
    set_tenant_from_restaurant(restaurant)
    time_seconds = settings.MAX_TIME['notif_client_rejet_commande']*60
    time.sleep(time_seconds)

    commande = Commande.objects.get(pk=commande.id, is_active=True, is_deleted=False)

    if commande.is_restaurant_valid is not True and commande.is_delivery_valid is not True:
        commande.is_active = False
        commande.is_deleted = True
        commande.save()
        subject = 'Rejet de la commande'
        message_sms = "Hello! C'est WaziEats, \nMalheureusement, votre commande " + str(commande.reference) + " ne sera pas traitée car le délai de validation est passée.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, votre commande " + str(commande.reference) + " ne sera pas traitée car le délai de validation est passée.\nMerci de nous faire confiance."
        en_tete = 'Rejet de la commande'
        flag = 1
        notifications_message(request, client, subject, message_sms, message_mail, en_tete, flag)
    if commande.is_restaurant_valid is True:
        subject = 'Rejet de la commande'
        message_sms = "Hello! C'est WaziEats, \nMalheureusement, aucun livreur n'est disponible pour valider la livraison de la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, Aucun livreur n'est disponible pour valider la livraison de la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        en_tete = 'Rejet de la commande'
        flag = 0
        notifications_message(request, commande.restaurant_validated_by, subject, message_sms, message_mail, en_tete, flag)
    elif commande.is_delivery_valid is True:
        subject = 'Rejet de la commande'
        message_sms = "Hello! C'est WaziEats, \nMalheureusement, le restaurant n'a pas validé la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, le restaurant n'a pas validé la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        en_tete = 'Rejet de la commande'
        flag = 0
        notifications_message(request, commande.delivery_validated_by, subject, message_sms, message_mail, en_tete, flag)


def notif_cancel_suggest_commande(request, commande, restaurant):
    """DocString."""
    set_tenant_from_restaurant(restaurant)
    time_seconds = settings.MAX_TIME['notif_client_rejet_commande']*60
    time.sleep(time_seconds)

    if commande.is_restaurant_valid is not True:
        commande.is_active = False
        commande.is_deleted = True
        commande.save()
        subject = 'Annulation de la commande'
        message_sms = "Hello! C'est WaziEats, \nMalheureusement, votre commande " + str(commande.reference) + " ne sera pas traitée car le délai de validation de la suggestion est passée.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, votre commande " + str(commande.reference) + " ne sera pas traitée car le délai de validation de la suggestion est passée.\nMerci de nous faire confiance."
        en_tete = 'Annulation de la commande'
        flag = 1
        notifications_message(request, commande.created_by, subject, message_sms, message_mail, en_tete, flag)
        subject = 'Annulation de la commande'
        message_sms = "Hello! C'est WaziEats, \nMalheureusement, le client n'a pas validé la suggestion de la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        message_mail = "Malheureusement, le client n'a pas validé la suggestion de la commande " + str(commande.reference) + ". Nous devons l'annuler.\nMerci de nous faire confiance."
        en_tete = 'Annulation de la commande'
        flag = 0
        notifications_message(request, commande.restaurant_suggest_by, subject, message_sms, message_mail, en_tete, flag)
