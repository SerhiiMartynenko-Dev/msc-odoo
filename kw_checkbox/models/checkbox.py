import json
import logging
import os
from datetime import datetime

import requests
from odoo import exceptions, _

_logger = logging.getLogger(__name__)

DATETIME_PATTERNS = ['%Y-%m-%dT%H:%M:%S.%f+00:00', '%Y-%m-%dT%H:%M:%S+00:00', ]


def get_datetime_from_format(date_str, date_patterns=None):
    date_patterns = date_patterns or DATETIME_PATTERNS
    for pattern in date_patterns:
        try:
            return datetime.strptime(date_str, pattern)
        except Exception as e:
            _logger.debug('%s', e)
    return None


def replace_response_date(value):
    if isinstance(value, list):
        res = []
        for val in value:
            res.append(replace_response_date(val))
    elif isinstance(value, dict):
        res = {}
        for k, val in value.items():
            res[k] = replace_response_date(val)
    else:
        val = get_datetime_from_format(value)
        res = val if val else value
    return res


class CheckBoxApi:
    username = ''
    password = ''
    access_token = ''
    license_key = ''
    test_mode = False

    def __init__(self, username='', password='', license_key='',
                 test_mode=False, access_token=''):
        self.username = username
        self.password = password
        self.access_token = access_token
        self.license_key = license_key
        self.test_mode = test_mode

    def get_url(self, ext=''):
        url = 'https://{}api.checkbox.in.ua'.format(
            'dev-' if self.test_mode else '')
        return os.path.join(url.strip('/'), 'api/v1', ext.strip('/'))

    @staticmethod
    def headers():
        return {'Content-Type': 'application/json',
                'accept': 'application/json', }

    def auth_headers(self):
        headers = self.headers()
        headers['Authorization'] = 'Bearer %s' % self.access_token
        return headers

    def key_headers(self):
        headers = self.auth_headers()
        headers['X-License-Key'] = self.license_key
        return headers

    def request(self, method, url, data=None, params=None, headers=None):
        headers = getattr(self, headers or 'key_headers')()
        # _logger.info(self.get_url(url))
        # _logger.info(data)
        # _logger.info(json.dumps(data))
        # _logger.info(params)
        # _logger.info(json.dumps(params))
        res = requests.request(
            method=method, url=self.get_url(url), data=data, params=params,
            headers=headers)
        if 200 > res.status_code or res.status_code > 300:
            try:
                res = res.json()
                if res.get('message'):
                    raise exceptions.ValidationError(res.get('message'))
            except Exception as e:
                _logger.debug('%s', e)
                # _logger.info('%s', e)
                raise exceptions.ValidationError(
                    _('Checkbox error: "%s"') % e)
        # _logger.info(res.text)
        res = res.json()
        return replace_response_date(res)

    def get(self, url, params=None, headers=None):
        return self.request('get', url=url, params=params, headers=headers)

    def post(self, url, data=None, headers=None):
        return self.request('post', url=url, data=data, headers=headers)

    def cashier_signin(self):
        if not (self.username and self.password):
            raise exceptions.UserError(
                _('Checkbox username or password might be empty'))
        res = self.post(
            url='/cashier/signin', headers='headers',
            data=json.dumps({'login': str(self.username),
                             'password': str(self.password)}), )
        self.access_token = res['access_token']
        return self.access_token

    def shift_get(self):
        return self.get('/cashier/shift')

    def shifts_get(self, params):
        return self.get('/shifts', params)

    def shift_open(self):
        return self.post('/shifts')

    def shift_info(self, shift_id):
        return self.get('/shifts/%s' % shift_id)

    def shift(self):
        return (self.shift_get() or self.shift_open()).get('id')

    def cashier_me(self):
        return self.get('/cashier/me')

    def get_cash_registers(self, cash_register_id):
        return self.get('/cash-registers/{}'.format(cash_register_id))

    def cash_registers_ask_offline_codes(self, params):
        return self.get('/cash-registers/ask-offline-codes',
                        params=params)

    def cash_registers_get_offline_codes(self, params):
        return self.get('/cash-registers/get-offline-codes',
                        params=params)

    def cash_registers_get_offline_time(self, params):
        return self.get('/cash-registers/get-offline-time',
                        params=params)

    def cash_registers_check_offline_time(self, params):
        return self.get('/cash-registers/check-offline-time',
                        params=params)

    def cash_registers_ping_tax_service(self):
        return self.post('/cash-registers/ping-tax-service')

    def get_all_tax(self):
        return self.get('/tax')

    def cash_registers_info(self):
        return self.get('/cash-registers/info')

    def go_online(self):
        return self.post('/cash-registers/go-online')

    def go_offline(self):
        return self.post('/cash-registers/go-offline')

    def shift_close(self):
        return self.post('/shifts/close')

    def receipts_sell(self, payload):
        return self.post('/receipts/sell', data=json.dumps(payload))

    def receipts_sell_offline(self, payload):
        return self.post('/receipts/sell-offline', data=json.dumps(payload))

    def receipt(self, receipt_id):
        return self.get('/receipts/%s' % receipt_id)

    def receipt_text(self, receipt_id):
        return requests.get(
            self.get_url('/receipts/%s/text' % receipt_id),
            headers=self.auth_headers()).content

    def receipt_html(self, receipt_id):
        return requests.get(
            self.get_url('/receipts/%s/html' % receipt_id),
            headers=self.auth_headers()).content

    def wait_receipt_done(self, receipt_id):
        res = self.receipt(receipt_id)
        while res['transaction']['status'] != 'DONE':
            res = self.receipt(receipt_id)
        return res

    # GET X report
    def x_report(self):
        return self.post('/reports')
