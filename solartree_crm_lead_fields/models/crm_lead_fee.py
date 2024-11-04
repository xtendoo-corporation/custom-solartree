from odoo import fields, models

class CrmLeadFee(models.Model):
    _name = "crm.lead.fee"
    _description = "Lead Fee"

    name = fields.Char(
        string="Fee Name",
        required=True
    )
