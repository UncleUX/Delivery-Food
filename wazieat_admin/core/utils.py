from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_mail(request, to_email, title, text_content=None, html_content=None):
    """Docstring for send_mail."""
    if to_email is not None:
        from_email = settings.APP['email']['from']
        msg = EmailMultiAlternatives(
            title,
            text_content,
            from_email,
            [to_email]
        )
        if html_content:
            msg.attach_alternative(html_content, 'text/html')

        msg.send()

