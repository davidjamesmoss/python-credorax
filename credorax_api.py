import uuid
import hashlib
from cgi import parse_qs
from decimal import Decimal, InvalidOperation
import requests
from requests.exceptions import Timeout, ConnectionError


class CredoraxConnectionError(Exception):
    pass


class CredoraxCardDeclinedError(Exception):
    pass


class CredoraxRequestError(Exception):
    def __init__(self, response):
        super(CredoraxRequestError, self).__init__(response)
        self.response = response


class Credorax():

    def generate_payment_refernece(self):
        return str(uuid.uuid4()).replace('-', '')[:30]

    def prep_for_md5(self, input):
        s = str(input)
        s = "".join(filter(lambda x: ord(x) < 128, s))
        s = s.replace('<', ' ')
        s = s.replace('>', ' ')
        s = s.replace('"', ' ')
        s = s.replace('\'', ' ')
        s = s.replace('(', ' ')
        s = s.replace(')', ' ')
        s = s.replace('\\', ' ')
        return s.strip()

    def sign_payment_data(self, payment_data):
        out = []
        # Data must be in alphabetical order, capitals first for the MD5 hash
        for key in sorted(payment_data.iterkeys()):
            s = self.prep_for_md5(payment_data[key])
            out.append(s)

        md5_source = '%s%s' % (''.join(out), self.signature_key)
        payment_data['K'] = hashlib.md5(md5_source).hexdigest()
        return payment_data

    def process_result(self, result):
        response = parse_qs(result)
        vals = {}

        try:
            vals['payment_ref'] = response['a1'][0]
        except KeyError:
            pass

        try:
            vals['amount'] = Decimal(Decimal(response['a4'][0]) / 100)
        except (KeyError, InvalidOperation):
            pass

        try:
            vals['trans_ref'] = response['z13'][0]
        except KeyError:
            pass

        try:
            vals['response_id'] = response['z1'][0]
        except KeyError:
            pass

        try:
            vals['response_code'] = response['z2'][0]
        except KeyError:
            pass

        try:
            vals['response_msg'] = response['z3'][0]
        except KeyError:
            pass

        try:
            vals['auth_code'] = response['z4'][0]
        except KeyError:
            pass

        try:
            vals['reason_code'] = response['z6'][0]
        except KeyError:
            pass

        error_responses = {
            '05': 'declined',
            'N0': 'declined',
            'N1': 'declined',
            'N2': 'declined',
            'N3': 'declined',
            'N4': 'declined',
            'N5': 'declined',
            'N6': 'declined',
            'N7': 'declined',
            'N8': 'declined',
            'N9': 'declined',
            'N10': 'declined',
            '54': 'expired',
            '04': 'fraud',
            '12': 'fraud',
            '34': 'fraud',
            '41': 'fraud',
            '59': 'fraud',
            'J': 'fraud',
            '51': 'funds',
            '61': 'limit',
            '62': 'restricted',
        }

        # 0 response means it worked.
        # <0 response is invalid data or processing error
        # >0 is a decline.
        if vals['response_code'] == '0' or vals['response_code'] == '00':
            vals['approved'] = True
        else:
            response_code = int(vals['response_code'])
            if response_code < 0:
                raise CredoraxRequestError(vals)
            else:
                vals['failure_reason'] = error_responses[vals['reason_code']]
                raise CredoraxCardDeclinedError(vals)

        return vals

    def charge(self, data):
        payment_data = {
            'M': self.mid,
            'O': 1,
            'a1': self.generate_payment_refernece(),
            'a2': 2,
            'a4': int(data['amount'] * 100),  # in pence/cents
            'a5': data['currency'],
            'b1': data['card_number'],
            'b3': data['expiry_month'],
            'b4': data['expiry_year'],
            'b5': data['cvc2'],
            'c1': data['card_name'],
            'c3': data['email'],
            'c7': data['city'],
            'c9': data['country'],
            'c10': data['postcode'],
            'd1': data['ip_address'],
            # The d2 field must be present for tests to be approved.
            'd2': 'approve',
        }
        payment_data = self.sign_payment_data(payment_data)

        try:
            r = requests.post(self.api_url, data=payment_data, timeout=80)
            return self.process_result(r.text)
        except (Timeout, ConnectionError):
            raise CredoraxConnectionError('Could not connect to API endpoint')

    def refund(self, data):
        payment_data = {
            'M': self.mid,
            'O': 7,
            'a1': self.generate_payment_refernece(),
            'a2': 2,
            'd1': data['ip_address'],
            'g2': data['previous_response_id'],
            'g3': data['previous_auth_code'],
            'g4': data['previous_request_id'],
        }
        payment_data = self.sign_payment_data(payment_data)

        try:
            r = requests.post(self.api_url, data=payment_data, timeout=80)
            return self.process_result(r.text)
        except (Timeout, ConnectionError):
            raise CredoraxConnectionError('Could not connect to API endpoint')
