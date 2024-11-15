from odoo import fields, models

class CrmLead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    solartree_lead_channel = fields.Many2one(
        related='lead_id.solartree_lead_channel',
        comodel_name='crm.lead.channel',
        string='Lead Channel',
        readonly=False
    )
    solartree_lead_identification = fields.Char(
        related='lead_id.solartree_lead_identification',
        string='Lead Identification',
        readonly=False
    )
    solartree_date_request = fields.Date(
        related='lead_id.solartree_date_request',
        string='Date Request',
        default=fields.Date.context_today,
        store=True,
        readonly=False,
    )

