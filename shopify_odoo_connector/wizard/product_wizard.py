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


class ProductWizard(models.TransientModel):
    _name = 'product.wizard'
    _description = 'Product Wizard'

    import_products = fields.Selection(string='Import/Export',
                                       selection=[('shopify', 'To Shopify'),
                                                  ('odoo', 'From Shopify')],
                                       required=True, default='shopify')
    shopify_instance = fields.Many2one('shopify.configuration',
                                       string="Shopify Instance", required=True)

    def sync_products(self):
        api_key = self.shopify_instance.con_endpoint
        PASSWORD = self.shopify_instance.consumer_key
        store_name = self.shopify_instance.shop_name
        version = self.shopify_instance.version

        if self.import_products == 'shopify':
            product_url = "https://%s:%s@%s/admin/api/%s/products.json" % (
                api_key, PASSWORD, store_name, version)
            product = self.env['product.template'].search([])
            for rec in product:
                if not rec.synced_product:
                    rec.synced_product = True
                    variants = []
                    for line in rec.attribute_line_ids.value_ids:
                        line_vals = {
                            "option1": line.name,
                            "price": rec.list_price,
                            "sku": rec.qty_available
                        }
                        variants.append(line_vals)
                    product_attribute = self.env['product.attribute']
                    options = []
                    for line in rec.attribute_line_ids:
                        vals = {
                            "name": line.attribute_id.name,
                            "values": variants
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
        else:
            product_url = "https://%s:%s@%s/admin/api/%s/products.json" % (
                api_key, PASSWORD, store_name, version)
            payload = []
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", product_url,
                                        headers=headers,
                                        data=payload)
            j = response.json()
            print('produt from wizard', j, '####', j['products'])
            for each in j['products']:
                existing_product = self.env['product.template'].search(
                    [('name', '=', each['title'])])
                if not existing_product:
                    vals = {
                        "name": each['title'],
                        "type": 'product',
                        "categ_id": self.env.ref(
                            'product.product_category_all').id,
                        "synced_product": True
                    }
                    product = self.env['product.template']
                    product.create(vals)
