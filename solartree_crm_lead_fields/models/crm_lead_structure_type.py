from odoo import fields, models

class CrmLeadStructureType(models.Model):
    _name = "crm.lead.structure.type"
    _description = "Lead Structure type"

    name = fields.Char(
        string="Structure Type Name",
        required=True
    )
