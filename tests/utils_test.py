from pytest_mock import MockerFixture

from utils import send_order_email


class TestUtils:
    def test_send_order_email(self, mocker: MockerFixture):
        order_form = {
            "name": "Jane",
            "last_name": "Doe",
            "address": "Barcelona, CP 08001",
            "email": "jane.doe@gmail.com",
            "mobile_number": "+34123456789"
        }

        mock_send_mail = mocker.patch("utils.send_mail")

        assert send_order_email(order_form) is None

        subject = "Your order has been send"
        message = "Hi Jane Doe, your order has been send to Barcelona, CP 08001. We will reach out to you at number " \
                  "+34123456789 in case of a delay."
        mock_send_mail.assert_called_once_with(subject, message, "shopping_cart@gmail.com", ["jane.doe@gmail.com"])
