from odoo import models, fields, api

class ContactProfile(models.Model):
    _name = "contact.profile"
    _description = "Contact Profile"

    name = fields.Char(
        string="Name"
    )
