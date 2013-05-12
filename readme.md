# Python-Credorax

Python library for the Credorax payment gateway.  
Supports basic charges and full refunds only, but easily extended.

[Credorax API Docs (PDF)](https://base2.credorax.com/intenv/service/pdf)

### Caveats
- This was extracted from a Django app and heavily refactored. I have only done basic checks to make sure it works, so your mileage may vary.  
- Doesn’t validate any of the inputs. That’s up to you.  
- The code for handling failed responses in particular may not be suitable for your needs.  
- To pass Credorax certification you need to complete a series of (trivial) tests which would require you to edit this library to use function calls that are otherwise hard-coded.

### Usage
	from credorax_api import Credorax
	from decimal import Decimal
	
	c = Credorax()
	c.mid = 'YOUR_MID_HERE'
	c.signature_key = 'YOUR_KEY_HERE'
	c.api_url = 'https://your-url-here.com'

	response = c.charge({
		'amount': Decimal(100.00),
		'currency': 'EUR',  # only EUR supported for testing.
		'card_number': '4242424242424242',
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

Would respond with:

	{
		'reason_code': u'00',
		'response_code': u'0',
		'auth_code': u'123456',
		'amount': Decimal('100'),
		'response_id': u'190817',
		'response_msg': u'APPROVED',
		'trans_ref': u'2315868160001700',
		'approved': True,
		'payment_ref': u'875b87843f1543e08d72ad0aa41ec9'
	}


Make sure you save at least the payment\_ref, response\_id and auth\_code as you’ll need them to make refunds.

To refund:

	c.refund({
		'previous_response_id': response['response_id'],
		'previous_auth_code': response['auth_code'],
		'previous_request_id': response['payment_ref'],
		'ip_address': '127.0.0.1',
	})

### Exceptions
If there is a failure connecting to the API endpoint, a CredoraxConnectionError is raised.  
If your request is invalid, a CredoraxRequestError is raised.  
If the card is declined, a CredoraxCardDeclinedError is raised.
	
Example CredoraxRequestError response

	CredoraxRequestError: {
		'response_code': u'-9',
		'response_msg': u'Wrong transaction currency [ABC] for merchant [200]'
	}

Example CredoraxCardDeclinedError response

	CredoraxCardDeclinedError: {
		'reason_code': u'05',
		'response_code': u'1',
		'auth_code': u'000000',
		'failure_reason': 'declined',
		'amount': Decimal('100'),
		'response_id': u'190827',
		'response_msg': u'NOT APPROVED',
		'trans_ref': u'2315868160001700',
		'payment_ref': u'f3a7f7c4b5274077a84be1ef6885b4'
	}


### Tests

Some rudimentary tests to check that a charge is successful, that an incorrect currency code raises an error and that a refund works.  
You’ll need to edit tests.py with your merchant ID and key.

### Requirements
- [Requests](http://docs.python-requests.org/en/latest/index.html)