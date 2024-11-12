from odoo import fields, models

class CrmLeadTot(models.Model):
    _name = "crm.lead.tot"
    _description = "Lead Tot"

    name = fields.Char(
        string="Tot Name",
        required=True
    )
