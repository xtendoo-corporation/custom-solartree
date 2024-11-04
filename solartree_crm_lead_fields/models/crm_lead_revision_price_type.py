from odoo import fields, models

class CrmLeadRevisionPrices(models.Model):
    _name = "crm.lead.revision.price.type"
    _description = "Lead Revision Prices"

    name = fields.Char(
        string="Name",
        required=True
    )

    type = fields.Selection(
        [
            ('euro', 'Euro'),
            ('percentage', 'Percentage')
        ],
        string="Type",
        required=True
    )
