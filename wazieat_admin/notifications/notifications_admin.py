from django.template.loader import render_to_string
from core.utils import send_mail
import requests
import json
import logging
from django.conf import settings
import base64
from twilio.rest import Client


logger = logging.getLogger("myLogger")

"""
def send_sms_code(request, user):
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

    url = "https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B" + str(devPhoneNumber)[1:] + "/requests"
    body = {
        "outboundSMSMessageRequest": {
            "address": "tel:" + str(user.phone),
            "senderAddress": "tel:" + str(devPhoneNumber),
            "outboundSMSTextMessage": {
                "message": "Hello! C'est WaziEats, \nVous avez une demande d'un nouveau compte restaurant à traiter.\n\nCordialement"
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


def send_sms_code(request, user):
    client_id = settings.TWILIO_SID

    client_secret = settings.TWILIO_AUTH

    code = client_id + ":" + client_secret

    devPhoneNumber = settings.TWILIO_PHONE_NUMBER

    client = Client(client_id, client_secret)

    try:
        sms = client.messages.create(
            body="Hello! C'est WaziEats, \nVous avez une demande d'un nouveau compte restaurant à traiter.\n\nCordialement",
            from_=devPhoneNumber,
            to=str(user.phone)
        )
        logger.info(
                "SMS Envoyé avec le ID " + sms.sid,
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )
    except Exception as e:
        print(str(e))
        logger.info(
                "Impossible d'envoyer de SMS!",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )


def send_mail_code(request, user, type1, name, email):

    url = settings.APP['admin_url'] + 'login'

    context = {
        'type': type1,
        'site_name': settings.APP['site_name'],
        'name': name,
        'email': email,
        'url': url
    }
    html_content = render_to_string(
        'email/accounts/notif_admin.html',
        context
    )
    text_content = render_to_string(
        'email/accounts/notif_admin.txt',
        context
    )

    subject = 'Nouveau compte ' + type1

    send_mail(request, user.email, subject, text_content, html_content)


def notifications_admin(request, user, type1, name, email):
    send_sms_code(request, user)
    if user.email is not None:
        send_mail_code(request, user, type1, name, email)
