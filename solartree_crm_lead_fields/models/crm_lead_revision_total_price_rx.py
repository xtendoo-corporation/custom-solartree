from odoo import fields, models

class CrmLeadRevisionTotalPriceRX(models.Model):
    _name = "crm.lead.revision.total.price.rx"
    _description = "Lead Revision Total Price RX"

    name = fields.Char(
        string="Name",
        required=True
    )
