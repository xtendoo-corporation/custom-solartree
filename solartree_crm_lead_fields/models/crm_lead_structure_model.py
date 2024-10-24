from odoo import fields, models

class CrmLeadStructureModel(models.Model):
    _name = "crm.lead.structure.model"
    _description = "Lead Structure model"

    name = fields.Char(
        string="Structure Model Name",
        required=True
    )
