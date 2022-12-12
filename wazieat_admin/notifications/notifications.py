from django.template.loader import render_to_string
from core.utils import send_mail
import requests
import json
import logging
import pyshorteners
from django.conf import settings
import base64
from twilio.rest import Client


logger = logging.getLogger("myLogger")

"""
def send_sms_code(request, user, compte_type):
    # send SMS
    access_token = None
    token_type = None
    url = "https://api.orange.com/oauth/v3/token"
    body = {
        "grant_type": "client_credentials"
    }
    headers = {'Authorization': 'Basic ODNmOEdvSWF5c3lVOWR0UHFzS1p0b2IxTlVjOUdwS1c6WHFFM050dWozTUJlMnA3VA=='}
    r = requests.post(url, data=json.dumps(body), headers=headers)
    if r.status_code == 200 or r.status_code == 201:
        res = r.json()
        access_token = res['access_token']
        token_type = res['token_type']
    else:
        if request.user.is_anonymous is False:
            logger.info(
                "Impossible de récupérer les credentials.",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
    if access_token is None:
        access_token = settings.ACCESS_TOKEN
        token_type = settings.TYPE_TOKEN

    devPhoneNumber = settings.WAZIEATS_PHONE_NUMBER

    url1 = settings.APP['site_url'] + 'init-account?token='
    url1 = url1 + str(user.reset_token)
    url1 = url1 + '&phone=' + str(user.phone)
    message = "Hello! C'est WaziEats,\n" + compte_type + \
              "\nCliquez sur ce lien pour activer votre compte " + url1 + "\nMerci de nous faire confiance."

    # message = "Hello! C'est WaziEats, \nUtilisez ce code " + str(user.reset_token) + "pour authentification."  "\nMerci de nous faire confiance."

    url = "https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B" + str(devPhoneNumber)[1:] + "/requests"
    body = {
        "outboundSMSMessageRequest": {
            "address": "tel:" + str(user.phone),
            "senderAddress": "tel:" + str(devPhoneNumber),
            "outboundSMSTextMessage": {
                "message": message
            }
        }
    }
    headers = {
        'Authorization': str(token_type) + ' ' + str(access_token),
        'Content-Type': "application/json",
        'Host': "api.orange.com"
    }
    r = requests.post(url, data=json.dumps(body), headers=headers)
    if r.status_code == 200 or r.status_code == 201:
        if request.user.is_anonymous is False:
            logger.info(
                "SMS envoyé avec succès.",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
    else:
        if request.user.is_anonymous is False:
            logger.info(
                "Impossible d'envoyer de SMS.",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
"""


def send_sms_code(request, user, compte_type):
    # send SMS

    client_id = settings.TWILIO_SID

    client_secret = settings.TWILIO_AUTH

    code = client_id + ":" + client_secret

    devPhoneNumber = settings.TWILIO_PHONE_NUMBER

    url1 = settings.APP['site_url'] + 'init-account?token='
    url1 = url1 + str(user.reset_token)
    url1 = url1 + '&phone=' + str(user.phone)
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(url1)

    message = "Hello! C'est WaziEats,\n" + compte_type + \
              "\nCliquez sur ce lien pour activer votre compte " + short_url + "\nMerci de nous faire confiance."

    client = Client(client_id, client_secret)

    try:
        sms = client.messages.create(
            body=message,
            from_=devPhoneNumber,
            to=str(user.phone)
        )
        if request.user.is_anonymous is False:
            logger.info(
                "SMS Envoyé avec le ID " + sms.sid,
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )
    except Exception as e:
        if request.user.is_anonymous is False:
            logger.info(
                "Impossible d'envoyer de SMS.",
                extra={
                    'restaurant': request.user.restaurant,
                    'user': request.user.id
                }
            )


def send_mail_code(request, user, compte_type):
    site_url = settings.APP['site_url']
    login_url = settings.APP['site_url'] + 'login'
    url = settings.APP['site_url'] + 'init-account?token='
    url = url + str(user.reset_token)
    url = url + '&phone=' + str(user.phone)

    context = {
        'phone': user.phone,
        'login_url': login_url,
        'site_name': settings.APP['site_name'],
        'site_url': site_url,
        'url': url,
        'compte_type': compte_type
    }
    html_content = render_to_string(
        'email/accounts/new_user.html',
        context
    )
    text_content = None
    """text_content = render_to_string(
        'email/accounts/new_user.txt',
        context
    )"""

    subject = 'Message de bienvenue'

    send_mail(request, user.email, subject, text_content, html_content)


def notifications(request, user):
    if user.delivery is not None:
        compte_type = "Vous avez fait une demande de création d'un compte livreur."
    elif user.is_client is not None:
        compte_type = "Vous avez fait une demande de création d'un compte client."
    elif user.restaurant is not None:
        if user.is_staff is True:
            compte_type = "Un compte admin restaurant a été créé pour vous."
        else:
            compte_type = "Un compte utilisateur restaurant a été créé pour vous."
    else:
        compte_type = "Un compte admin Wazieats a été créé pour vous."
    send_sms_code(request, user, compte_type)
    if user.email is not None:
        send_mail_code(request, user, compte_type)
