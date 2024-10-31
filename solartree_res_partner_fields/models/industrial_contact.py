from odoo import models, fields, api

class IndustrialContact(models.Model):
    _name = "industrial.contact"
    _description = "Industrial Contact"

    name = fields.Char(
        string="Name"
    )
