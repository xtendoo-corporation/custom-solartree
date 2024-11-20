from odoo import models, fields

class OfferClass(models.Model):
    _name = 'offer.class'
    _description = 'Offer Class'

    name = fields.Char(
        string='Offer Class'
    )
    min_value = fields.Integer(
        string='Min Value'
    )
    max_value = fields.Integer(
        string='Max Value'
    )
    structure_expenses = fields.Float(
        string='Structure Expenses %'
    )
    industrial_profit = fields.Float(
        string='Industrial Profit %'
    )
