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

{
    'name': "Shopify Odoo Connector",
    'version': '15.0.1.0.0',
    'summary': """Shopify Odoo Connector enables users to connect with shopify 
    to odoo and sync sale orders, customers and products""",
    'description': """Shopify Odoo Connector, Odoo Shopify Connector, Shopify, 
    Shopify Odoo Connector enables users to connect with shopify to odoo and 
    sync sale orders, customers and products, connector""",
    'category': 'Sales/Sales',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['sale_management',
                'stock',
                ],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/shopify.xml',
        'wizard/product_wizard.xml',
        'wizard/customer_wizard.xml',
        'wizard/order_wizard.xml',
    ],
    'license': 'OPL-1',
    'price': 49,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False
}
