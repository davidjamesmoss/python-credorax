import unittest
from decimal import Decimal
from credorax_api import Credorax, CredoraxRequestError


class CredoraxTests(unittest.TestCase):
    c = Credorax()
    c.mid = 'YOUR_MID_HERE'
    c.signature_key = 'YOUR_KEY_HERE'

    # Integration Environment URL
    c.api_url = 'https://base2.credorax.com/intenv/service/gateway'

    def test_successful_charge(self):
        response = self.c.charge({
            'amount': Decimal(100.00),
            'currency': 'EUR',  # only EUR supported for testing.
            'card_number': '4111111111111111',
            'expiry_month': '01',  # 2 chars with leading zero
            'expiry_year': '16',  # 2 chars with leading zero
            'cvc2': '123',
            'card_name': 'Mr A N other',
            'email': 'test@example.com',
            'city': 'Edinburgh',
            'country': 'GB',  # ISO 2-char code
            'postcode': 'EH1 1AA',
            'ip_address': '127.0.0.1',
        })
        self.assertTrue(isinstance(response, dict))

    def test_failed_charge(self):
        data = {
            'amount': Decimal(100.00),
            'currency': 'abc',  # invalid currency raises -9 error.
            'card_number': '4111111111111111',
            'expiry_month': '01',  # 2 chars with leading zero
            'expiry_year': '16',  # 2 chars with leading zero
            'cvc2': '123',
            'card_name': 'Mr A N other',
            'email': 'test@example.com',
            'city': 'Edinburgh',
            'country': 'GB',  # ISO 2-char code
            'postcode': 'EH1 1AA',
            'ip_address': '127.0.0.1',
        }

        self.assertRaises(CredoraxRequestError, self.c.charge, data)

    def test_successful_refund(self):
        response = self.c.charge({
            'amount': Decimal(100.00),
            'currency': 'EUR',  # only EUR supported for testing.
            'card_number': '4111111111111111',
            'expiry_month': '01',  # 2 chars with leading zero
            'expiry_year': '16',  # 2 chars with leading zero
            'cvc2': '123',
            'card_name': 'Mr A N other',
            'email': 'test@example.com',
            'city': 'Edinburgh',
            'country': 'GB',  # ISO 2-char code
            'postcode': 'EH1 1AA',
            'ip_address': '127.0.0.1',
        })
        self.c.refund({
            'previous_response_id': response['response_id'],
            'previous_auth_code': response['auth_code'],
            'previous_request_id': response['payment_ref'],
            'ip_address': '127.0.0.1',
        })

        self.assertTrue(isinstance(response, dict))

if __name__ == '__main__':
    unittest.main()
