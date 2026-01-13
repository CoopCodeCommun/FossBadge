import os

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string, get_template


class Mailer:
    """
    Class for sending emails.
    It should exclusively be used with celery ! (see tasks.py)
    """


    def __init__(self, subject, message, receiver_email, html_template=None, context=None):
        self.subject = subject
        self.message = message
        self.receiver_email = receiver_email
        if not isinstance(self.receiver_email, (tuple,list)):
            self.receiver_email = [self.receiver_email]

        if html_template and context:
            self.html = render_to_string(html_template, context=context)

        self.sender_email = os.environ.get('EMAIL_HOST_USER')

    def send(self):
        """
        Send the email
        """

        mail = EmailMultiAlternatives(
            subject=self.subject,
            body=self.message,
            from_email=self.sender_email,
            to=self.receiver_email,
        )

        #Attach the html
        mail.attach_alternative(self.html, "text/html")

        mail_success = mail.send()

        return mail_success
