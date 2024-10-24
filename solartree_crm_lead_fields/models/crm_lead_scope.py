from odoo import fields, models

class CrmLeadScope(models.Model):
    _name = "crm.lead.scope"
    _description = "Lead Scope"

    name = fields.Char(
        string="Scope Name",
        required=True
    )
