from odoo import fields, models

class CrmLeadTensionLevel(models.Model):
    _name = "crm.lead.tension.level"
    _description = "Lead Tension Level"

    name = fields.Char(
        string="Tension Level Name",
        required=True
    )
