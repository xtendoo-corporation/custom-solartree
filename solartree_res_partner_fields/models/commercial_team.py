from odoo import models, fields, api

class CommercialTeam(models.Model):
    _name = "commercial.team"
    _description = "Commercial Team"

    name = fields.Char(
        string="Name"
    )
