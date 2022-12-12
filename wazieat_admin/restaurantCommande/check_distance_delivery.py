from django.conf import settings
from notifications.notifications_message import notifications_message
import time


def check_distance_delivery(request, commande, client):
    """DocString."""
    time_seconds = 10*60
    time.sleep(time_seconds)

    location = request.user.delivery.location
    center_point = [{'lat': commande.delivery_location[0], 'lng': commande.delivery_location[1]}]
    radius = settings.RADIUS_NOTIF_CLIENT/1000  # in kilometer
    test_point = [{'lat': location[0], 'lng': location[1]}]
    center_point_tuple = tuple(center_point[0].values())  # (-7.7940023, 110.3656535)
    test_point_tuple = tuple(test_point[0].values())  # (-7.79457, 110.36563)

    dis = distance.distance(center_point_tuple, test_point_tuple).km
    print("Distance: {}".format(dis))  # Distance: 0.0628380925748918

    while dis > radius:
        time.sleep(time_seconds)

        location = request.user.delivery.location
        test_point = [{'lat': location[0], 'lng': location[1]}]
        center_point_tuple = tuple(center_point[0].values())  # (-7.7940023, 110.3656535)
        test_point_tuple = tuple(test_point[0].values())  # (-7.79457, 110.36563)

        dis = distance.distance(center_point_tuple, test_point_tuple).km
        print("Distance: {}".format(dis))  # Distance: 0.0628380925748918

    if commande.token is not None:
        subject = 'Livraison imminente'
        message_sms = "Hello! C'est WaziEats, \nVotre livreur est proche du lieu de livraison. Veuillez vous rapprocher de ce lieu. "
        message_sms = message_sms + "Le code de retrait de la commande est " + str(commande.token) +".\nMerci de nous faire confiance."
        message_mail = "Votre livreur est proche du lieu de livraison. Veuillez vous rapprocher de ce lieu.\n\n"
        message_mail = message_mail + "Votre code de retrait de la commande est " + commande.token + ".\n"
        en_tete = 'Livraison imminente'
        flag = 1
        notifications_message(request, client, subject, message_sms, message_mail, en_tete, flag)
