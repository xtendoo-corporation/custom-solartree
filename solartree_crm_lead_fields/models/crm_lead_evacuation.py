from odoo import fields, models

class CrmLeadEvacuation(models.Model):
    _name = "crm.lead.evacuation"
    _description = "Lead Evacuation"

    name = fields.Char(
        string="Evacuation Name",
        required=True
    )
