from odoo import models, fields, api

class ColaboratorType(models.Model):
    _name = "colaborator.type"
    _description = "Colaborator Type"

    name = fields.Char(
        string="Name"
    )
