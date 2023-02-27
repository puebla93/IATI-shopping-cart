"""Module to define all the project utilities.
"""

from django.core.mail import send_mail


def send_order_email(order_form: dict) -> None:
    """Sends an email to the customer.
    """

    name = order_form["name"]
    last_name = order_form["last_name"]
    address = order_form["address"]
    email = order_form["email"]
    mobile_number = order_form["mobile_number"]

    subject = "Your order has been send"
    message = f"Hi {name} {last_name}, your order has been send to {address}. We will reach out to you at the number " \
              f"{mobile_number} in case of a delay."
    from_email = "shopping_cart@gmail.com"

    send_mail(subject, message, from_email, [email])
