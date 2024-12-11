from odoo import _, models, fields, api

class Stage(models.Model):
    _inherit = "crm.stage"

    allowed_groups = fields.Many2many(
        'res.groups',
        string='Grupos permitidos',
        domain=lambda self: [('category_id', '=', self.env.ref('solartree_crm_lead_automatization.module_category_solartree').id)]
    )

    user_offer_tot_required = fields.Boolean(
        string='Usuario OT requerido',
        default=False
    )

    user_id_required = fields.Boolean(
        string='Comercial requerido',
        default=False
    )

    margin_approval_required = fields.Boolean(
        string='Autorización de margen requerida',
        default=False
    )

    assignation_solartree_code = fields.Boolean(
        string='Asignación de código Solartree',
        default=False
    )
