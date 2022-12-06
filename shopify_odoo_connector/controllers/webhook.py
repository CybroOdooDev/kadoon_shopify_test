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

from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
import dateutil.parser
import odoo
import pytz
import logging

_logger = logging.getLogger(__name__)


class WebHook(http.Controller):
    @http.route('/products', type='json', auth='none', methods=['POST'],
                csrf=False)
    def get_webhook_url(self, *args, **kwargs):
        print('for product webhook********************888')
        try:
            request.env['product.template'].with_user(SUPERUSER_ID).create({
                "name": request.jsonrequest['title'],
                "type": 'product',
                "categ_id": request.env.ref('product.product_category_all').id,
                "synced_product": True
            })
            return {"Message": "Success"}
        except Exception as e:
            return {"Message": "Something went wrong"}

    @http.route('/customers', type='json', auth='none', methods=['POST'],
                csrf=False)
    def get_webhook_customer_url(self, *args, **kwargs):
        try:
            vals = {}
            if request.jsonrequest['addresses']:
                vals = {
                    "street": request.jsonrequest['addresses'][0].get(
                        'address1'),
                    "street2": request.jsonrequest['addresses'][0].get(
                        'address2'),
                    "city": request.jsonrequest['addresses'][0].get['city'],
                    "country_id": request.jsonrequest['addresses'][0].get[
                        'country'],
                    "zip": request.jsonrequest['addresses'][0].get['zip'],
                }
            vals["name"] = request.jsonrequest.get('first_name')
            vals["email"] = request.jsonrequest.get('email')
            vals["phone"] = request.jsonrequest.get('phone')
            vals["synced_customer"] = True
            request.env['res.partner'].with_user(SUPERUSER_ID).create(vals)
            return {"Message": "Success"}
        except Exception as e:
            return {"Message": "Something went wrong"}

    @http.route('/orders', type='json', auth='none', methods=['POST'],
                csrf=False)
    def get_webhook_order_url(self, *args, **kwargs):
        try:
            customer_name = request.jsonrequest['customer'].get('first_name')
            partner_id = request.env['res.partner'].with_user(
                SUPERUSER_ID).search([('name', '=', customer_name)]).id
            if not partner_id:
                partner_id = request.env['res.partner'].with_user(
                    SUPERUSER_ID).create({'name': customer_name}).id
            so = request.env['sale.order'].with_user(SUPERUSER_ID).create({
                "partner_id": partner_id,
                "date_order": odoo.fields.Datetime.to_string(
                    dateutil.parser.parse(
                        request.jsonrequest['created_at']).astimezone(
                        pytz.utc)),
                "l10n_in_gst_treatment": "regular",
                "shopify_order_id": request.jsonrequest['id'],
                "synced_order": True,
                "name": request.jsonrequest['name']
            })
            if request.jsonrequest['tax_lines']:
                tax = request.jsonrequest['tax_lines'][0]['rate']
                tax_group = request.jsonrequest['tax_lines'][0]["title"]
                taxes = tax * 100
                tax_name = request.env[
                    'account.tax'].with_user(SUPERUSER_ID).search(
                    [('amount', '=', taxes), ('tax_group_id', '=', tax_group),
                     ('type_tax_use', '=', 'sale')])
                if not tax_name:
                    tax_group_id = request.env['account.tax.group'].with_user(
                        SUPERUSER_ID).create({'name': tax_group})
                    tax_name = request.env['account.tax'].with_user(
                        SUPERUSER_ID).create(
                        {'name': tax_group + str(taxes) + '%',
                         'type_tax_use': 'sale',
                         'amount_type': 'percent',
                         'tax_group_id': tax_group_id.id,
                         'amount': taxes,
                         })
            else:
                tax_name = None
            if request.jsonrequest['line_items']:
                line_items = request.jsonrequest['line_items']
                for line in line_items:
                    product_name = line['title']
                    product_id = request.env['product.product'].with_user(
                        SUPERUSER_ID).search(
                        [('name', '=', product_name)]).id
                    if not product_id:
                        product_id = request.env['product.product'].with_user(
                            SUPERUSER_ID).create(
                            {'name': product_name}).id
                    line_values = {
                        "product_id": product_id,
                        "price_unit": line['price'],
                        "product_uom_qty": line['quantity'],
                        'order_id': so.id,
                        'tax_id': tax_name,
                    }
                    request.env['sale.order.line'].with_user(
                        SUPERUSER_ID).create(line_values)
            return {"Message": "Success"}
        except Exception as e:
            return {"Message": "Something went wrong"}
