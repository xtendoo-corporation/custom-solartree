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
    res_group_mail_ids = fields.Many2many(
        'res.groups',
        relation='offer_class_res_group_mail_rel',
        column1='offer_class_id',
        column2='group_id',
        string='Groups to send email',
        domain=lambda self: [('category_id', '=', self.env.ref('solartree_crm_lead_automatization.module_category_solartree').id)]
    )
    res_group_meet_ids = fields.Many2many(
        'res.groups',
        relation='offer_class_res_group_meet_rel',
        column1='offer_class_id',
        column2='group_id',
        string='Groups to meeting',
        domain=lambda self: [('category_id', '=', self.env.ref('solartree_crm_lead_automatization.module_category_solartree').id)]
    )
