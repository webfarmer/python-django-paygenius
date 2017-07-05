import hashlib
import hmac
import json
import requests
from django.core.urlresolvers import reverse

class PayGenius(object):
    DEBUG = True
    if DEBUG:
        validate_url = 'https://developer.paygenius.co.za/pg/api/v2/'
        x_token = ""
        x_secret = ""
    else:
        validate_url = 'https://www.paygenius.co.za/pg/api/v2/'
        x_token = ""
        x_secret = ""

    def send_request(self, url, data):
        new_url = url + "\n" + ("%s" % json.dumps(data))
        signature = hmac.new(self.x_secret, new_url, digestmod=hashlib.sha256).hexdigest()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Signature': signature,
            'X-Token': self.x_token,
        }
        r = requests.post(url, json=data, headers=headers)
        return r.json()

    def redirect(self, request, invoice, customer, amount):
        success_url = "http://%s%s" % (request.META['HTTP_HOST'], reverse("pg_success"))
        failed_url = "http://%s%s" % (request.META['HTTP_HOST'], reverse("pg_failed"))
        data = {
            "consumer": {
                "name": customer["first_name"],
                "surname": customer["last_name"],
                "email": customer["email"]
            },
            "transaction": {
                "description": request.GET.get("description", invoice["Reference"]),
                "reference": invoice["Reference"],
                "currency": "ZAR",
                "amount": (amount * 100)
            },
            "urls": {
                "success": "%s?reference=%s" % (success_url, invoice["InvoiceNumber"]),
                "cancel": "%s?reference=%s" % (failed_url, invoice["InvoiceNumber"]),
                "error": "%s?reference=%s" % (failed_url, invoice["InvoiceNumber"])
            }
        }
        payment_url = "%sredirect/create" % self.validate_url
        return self.send_request(payment_url, data=data)

    def redirect_lookup(self, reference):
        data = {}
        payment_url = "%sredirect/%s" % (self.validate_url, reference)
        return self.send_request(payment_url, data=data)

    def lookup(self, data):
        payment_url = "%scard/lookup" % self.validate_url
        return self.send_request(payment_url, data=data)

    def create_payment(self, data):
        payment_url = "%spayment/create" % self.validate_url
        return self.send_request(payment_url, data=data)

    def execute_payment(self, reference):
        payment_url = "%spayment/%s/execute" % (self.validate_url, reference)
        return self.send_request(payment_url, data=data)

