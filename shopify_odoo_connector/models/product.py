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

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_instance = fields.Many2one('shopify.configuration',
                                       string="Shopify Instance")
    synced_product = fields.Boolean(readonly=False, store=True)

    def sync_shopify_product(self):
        print("product")
        api_key = self.shopify_instance.con_endpoint
        PASSWORD = self.shopify_instance.consumer_key
        store_name = self.shopify_instance.shop_name
        version = self.shopify_instance.version

        product_url = "https://%s:%s@%s/admin/api/%s/products.json" % (
            api_key, PASSWORD, store_name, version)
        print(product_url, 'product_url')
        product = self.env['product.template'].search([('id', '=', self.id)])
        if not self.synced_product:
            print("1")
            self.synced_product = True
            variants = []
            for line in self.attribute_line_ids.value_ids:
                print("IN")
                print(self.attribute_line_ids.value_ids,
                      "self.attribute_line_ids.value_ids")
                line_vals = {
                    "option1": line.name,
                    "price": self.list_price,
                    "sku": self.qty_available,
                    "id": self.id,
                    "product_id": self.id,

                }
                variants.append(line_vals)
                print(line_vals, 'line_vals')
                _logger.info(variants)

            if not variants:
                line_vals = {
                    # "option1": line.name,
                    # "price": self.list_price,
                    # "sku": self.qty_available
                    "id": self.id,
                    "product_id": self.id,
                    "title": self.name,
                    "body_html": self.description_sale
                    if self.description_sale else '',
                    "price": self.list_price,
                    "sku": self.qty_available,
                    "unitCost": self.standard_price,
                    "product_type": 'Storable Product'
                    if self.type == 'product' else 'Consumable'
                    if self.type == 'consu' else 'Service',
                    "barcode": self.barcode if self.barcode else '',
                }
                variants.append(line_vals)

            # product_attribute = self.env['product.attribute']
            # options = []
            #
            # for rec in self.attribute_line_ids:
            #     vals = {
            #         "name": rec.attribute_id.name,
            #         "values": variants
            #     }
            #     options.append(vals)

            payload = json.dumps({
                "product": {
                    'id': self.id,
                    "title": self.name,
                    "body_html": self.description_sale
                    if self.description_sale else "",
                    "sku": self.qty_available,
                    # "quantity": self.qty_available,
                    "product_type": 'Storable Product'
                    if self.type == 'product' else 'Consumable'
                    if self.type == 'consu' else 'Service',
                    # "": self.categ_id,
                    "unitCost": self.standard_price,
                    "variants": variants,
                }
            })
            print(payload, "payload")
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", product_url, headers=headers,
                                        data=payload)
            print(response, 'response')
