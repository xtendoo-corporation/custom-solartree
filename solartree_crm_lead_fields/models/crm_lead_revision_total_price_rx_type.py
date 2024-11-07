from odoo import fields, models

class CrmLeadRevisionTotalPriceRXType(models.Model):
    _name = "crm.lead.revision.total.price.rx.type"
    _description = "Lead Revision Total Price RX Type"

    name = fields.Char(
        string="Name",
        required=True
    )
