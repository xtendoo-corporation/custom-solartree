from odoo import models, fields, api

class AssociatedCommercialChannel(models.Model):
    _name = "associated.commercial.channel"
    _description = "Associated Commercial Channel"

    name = fields.Char(
        string="Name"
    )
