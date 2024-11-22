from odoo import _, models, fields, api

class Stage(models.Model):
    _inherit = "crm.stage"

    allowed_groups = fields.Many2many(
        'res.groups',
        string='Allowed Groups',
        domain=lambda self: [('category_id', '=', self.env.ref('solartree_crm_lead_automatization.module_category_solartree').id)]
    )

    user_offer_tot_required = fields.Boolean(
        string='User tot required',
        default=False
    )#crm.lead.revision

    user_id_required = fields.Boolean(
        string='User required',
        default=False
    )#crm.lead

    margin_approval_required = fields.Boolean(
        string='Margin approval required',
        default=False
    )#crm.lead
