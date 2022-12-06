# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (Contact : odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################

from odoo import models, fields, api, _
import logging
import requests
import json
import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ShopifyConnector(models.Model):
    _name = 'shopify.configuration'
    _description = 'Shopify Connector'
    _rec_name = 'name'

    name = fields.Char(string='Instance Name', required=True)
    con_endpoint = fields.Char(string='API', required=True)
    consumer_key = fields.Char(string='Password', required=True)
    consumer_secret = fields.Char(string='Secret', required=True)
    shop_name = fields.Char(string='Store Name', required=True)
    version = fields.Char(string='Version', required=True)
    last_synced = fields.Datetime(string='Last Synced')
    state = fields.Selection([('new', 'Not Connected'),
                              ('sync', 'Connected'), ],
                             'Status', readonly=True, index=True, default='new')
    import_product = fields.Boolean(string='Import Products')
    import_customer = fields.Boolean(string='Import Customer')
    import_order = fields.Boolean(string='Import Orders')
    webhook_product = fields.Char(string='Product Url')
    webhook_customer = fields.Char(string='Customer Url')
    webhook_order = fields.Char(string='Order Url')

    def sync_shopify(self):

        api_key = self.con_endpoint
        PASSWORD = self.consumer_key
        # PASSWORD = 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
        # PASSWORD for devloper account = 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
        store_name = self.shop_name
        version = self.version

        url = "https://%s:%s@%s/admin/api/%s/storefront_access_tokens.json" % (
        api_key, PASSWORD, store_name, version)
        payload = json.dumps({
            "storefront_access_token": {
                "title": "Test"
            }
        })
        print('url', url)
        headers = {
            'Content-Type': 'application/json'

        }
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            self.state = "sync"

        else:
            raise ValidationError(
                _("Invalid Credentials provided .Please check them "))

    def sync_shopify_all(self):

        api_key = self.con_endpoint
        PASSWORD = self.consumer_key
        store_name = self.shop_name
        version = self.version

        if self.import_product == True:
            product_url = "https://%s:%s@%s/admin/api/%s/products.json" % (
                api_key, PASSWORD, store_name, version)
            print('producturl', product_url)
            self.ensure_one()
            if self.last_synced:
                product = self.env['product.template'].search(
                    [('create_date', '>=', self.last_synced)])
            else:
                product = self.env['product.template'].search([])
            for rec in product:
                if not rec.synced_product:
                    rec.synced_product = True
                    variants = []
                    for line in rec.attribute_line_ids.value_ids:
                        line_vals = {
                            "option1": line.name,

                        }
                        variants.append(line_vals)
                    product_attribute = self.env['product.attribute']
                    options = []

                    for line in rec.attribute_line_ids:
                        vals = {
                            "name": line.attribute_id.name,
                        }
                        options.append(vals)

                    payload = json.dumps({
                        "product": {
                            "title": rec.name,
                            "body_html": "",
                            "product_type": rec.type,
                            "variants": variants,
                            "options": options,

                        }
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", product_url,
                                                headers=headers,
                                                data=payload)
                    print('response', response)

        if self.import_customer == True:
            customer_url = "https://%s:%s@%s/admin/api/%s/customers.json" % (
                api_key, PASSWORD, store_name, version)
            if self.last_synced:
                partner = self.env['res.partner'].search(
                    [('create_date', '>=', self.last_synced)])
            else:
                partner = self.env['res.partner'].search([])
            for customer in partner:
                if not customer.synced_customer:
                    customer.synced_customer = True
                    payload = json.dumps({
                        "customer": {
                            "first_name": customer.name,
                            "last_name": "",
                            "email": customer.email,
                            "phone": customer.phone,
                            "verified_email": True,
                            "addresses": [
                                {
                                    "address1": customer.street,
                                    "city": customer.city,
                                    "province": "",
                                    "phone": customer.phone,
                                    "zip": customer.zip,
                                    "last_name": "",
                                    "first_name": customer.name,
                                    "country": customer.country_id.name
                                }
                            ],
                            "send_email_invite": True
                        }
                    })

                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", customer_url,
                                                headers=headers,
                                                data=payload)

        if self.import_order == True:
            order_url = "https://%s:%s@%s/admin/api/%s/draft_orders.json" % (
                api_key, PASSWORD, store_name, version)
            if self.last_synced:
                sale_order = self.env['sale.order'].search(
                    [('create_date', '>=', self.last_synced),
                     ('state', '=', 'draft')])
            else:
                sale_order = self.env['sale.order'].search(
                    [('state', '=', 'draft')])
            for order in sale_order:
                if not order.synced_order:
                    order.synced_order = True
                    line_items = []
                    for line in order.order_line:
                        line_vals = {
                            "title": line.product_id.name,
                            "price": line.price_unit,
                            "quantity": int(line.product_uom_qty),

                        }
                        line_items.append(line_vals)
                    payload = json.dumps({
                        "draft_order": {
                            "line_items": line_items,
                            "email": order.partner_id.email,
                            "use_customer_default_address": True
                        }
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", order_url,
                                                headers=headers,
                                                data=payload)
        self.last_synced = datetime.datetime.now()
