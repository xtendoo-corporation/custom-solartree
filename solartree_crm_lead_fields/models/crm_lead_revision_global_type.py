from odoo import fields, models

class CrmLeadRevisionPrices(models.Model):
    _name = "crm.lead.revision.global.type"
    _description = "Lead Revision Global Type"

    name = fields.Char(
        string="Name",
        required=True
    )

    behavior = fields.Selection(
        selection=[
            ('fee_and_margins', 'Fee and Margins'),
            ('total_price', 'Total Price')
        ],
        string="Behavior",
        required=True
    )
