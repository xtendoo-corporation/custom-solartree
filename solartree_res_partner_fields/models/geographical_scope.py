from odoo import api, fields, models

class GeographicalScope(models.Model):
    _name = "geographical.scope"
    _description = "Geographical Scope"

    name = fields.Char(
        string="Name"
    )
