from odoo import fields, models

class CrmLeadType(models.Model):
    _name = "crm.lead.type"
    _description = "Lead Type"

    name = fields.Char(
        string="Type Name",
        required=True
    )
