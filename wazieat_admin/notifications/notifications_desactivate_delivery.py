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
def send_sms_message(user, reason):
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
        logger.info(
            "Impossible de récupérer les credentials.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
    if access_token is None:
        access_token = settings.ACCESS_TOKEN
        token_type = settings.TYPE_TOKEN

    devPhoneNumber = settings.WAZIEATS_PHONE_NUMBER

    url = "https://api.orange.com/smsmessaging/v1/outbound/tel%3A%2B" + str(devPhoneNumber)[1:] + "/requests"
    message = "Votre compte a été désactivé.\n La raison du rejet est la suivante: \n"
    message = message + str(reason) + "\n\n" + "Veuillez nous contacter pour plus d'informations.\nMerci pour votre comprehension."
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
        logger.info(
            "SMS envoyé avec succès.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
    else:
        logger.info(
            "Impossible d'envoyer de SMS.",
            extra={
                'restaurant': user.restaurant,
                'user': user.id
            }
        )
"""


def send_sms_message(user, reason):
    client_id = settings.TWILIO_SID

    client_secret = settings.TWILIO_AUTH

    code = client_id + ":" + client_secret

    devPhoneNumber = settings.TWILIO_PHONE_NUMBER

    client = Client(client_id, client_secret)

    message = "Votre compte a été désactivé.\n La raison du rejet est la suivante: \n"
    message = message + str(reason) + "\n\n" + "Veuillez nous contacter pour plus d'informations.\nMerci pour votre comprehension."

    try:
        sms = client.messages.create(
            body=message,
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
        logger.info(
                "Impossible d'envoyer de SMS.",
                extra={
                    'restaurant': user.restaurant,
                    'user': user.id
                }
            )


def send_mail_message(request, user, reason):
    context = {
        'phone': user.phone,
        'site_name': settings.APP['site_name'],
        'reason': reason
    }

    subject = "Désactivation/Rejet du compte"

    html_content = render_to_string(
        'email/accounts/Desactivate_account.html',
        context
    )

    send_mail(request, user.email, subject, None, html_content)


def notifications(request, user, reason):
    send_sms_message(user, reason)
    if user.email is not None:
        send_mail_message(request, user, reason)
