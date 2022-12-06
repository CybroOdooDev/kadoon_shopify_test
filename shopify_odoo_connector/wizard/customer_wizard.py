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


from odoo import models, fields
import requests
import json


class CustomerWizard(models.TransientModel):
    _name = 'customer.wizard'
    _description = 'Customer Wizard'

    import_customers = fields.Selection(string='Import/Export',
                                        selection=[('shopify', 'To Shopify'),
                                                   ('odoo', 'From Shopify')],
                                        required=True, default='shopify')
    shopify_instance = fields.Many2one('shopify.configuration',
                                       string="Shopify Instance", required=True)

    def sync_customers(self):
        api_key = self.shopify_instance.con_endpoint
        PASSWORD = self.shopify_instance.consumer_key
        store_name = self.shopify_instance.shop_name
        version = self.shopify_instance.version

        if self.import_customers == 'shopify':
            customer_url = "https://%s:%s@%s/admin/api/%s/customers.json" % (
                api_key, PASSWORD, store_name, version)
            partner = self.env['res.partner'].search([])
            for customer in partner:
                if not customer.synced_customer:
                    customer.synced_customer = True
                    payload = json.dumps({
                        "customer": {
                            "first_name": customer.name,
                            "last_name": "",
                            "email": customer.email or '',
                            "verified_email": True,
                            "addresses": [
                                {
                                    "address1": customer.street,
                                    "city": customer.city,
                                    "province": "",
                                    "zip": customer.zip,
                                    "last_name": "",
                                    "first_name": customer.name,
                                    "country": customer.country_id.name or ''
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
        else:
            customer_url = "https://%s:%s@%s/admin/api/%s/customers.json" % (
                api_key, PASSWORD, store_name, version)
            payload = []
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", customer_url,
                                        headers=headers,
                                        data=payload)
            j = response.json()
            for each in j['customers']:
                name = each['first_name']
                if each['last_name']:
                    name = name + ' ' + each['last_name']
                existing_customer = self.env['res.partner'].search(
                    [('name', '=', name)])
                vals = {}
                email = each['email']
                if not existing_customer:
                    vals["name"] = each['first_name']
                    if each['last_name']:
                        vals["name"] = each['first_name'] + ' ' + each[
                            'last_name']
                    vals["email"] = each['email']
                    vals["phone"] = each['phone']
                    vals["ref"] = each['id']
                    vals["synced_customer"] = True
                    if each['addresses']:
                        for data in each['addresses']:
                            vals = {
                                "street": data['address1'],
                                "city": data['city'],
                                "zip": data['zip'],
                            }
                    partner = self.env['res.partner']
                    partner.create(vals)
