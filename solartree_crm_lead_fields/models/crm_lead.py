##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    solartree_code = fields.Char(
        string="Lead Code",
        required=True,
        copy=False
    )
    solartree_lead_type_id = fields.Many2one(
        comodel_name="crm.lead.type",
        string="Lead Type",
        help="Type of the lead"
    )
    solartree_lead_modality_id = fields.Many2one(
        comodel_name="crm.lead.modality",
        string="Lead Modality",
        help="Modality of the lead"
    )
    solartree_lead_collective = fields.Boolean(
        string="Lead Collective",
    )
    solartree_lead_storage = fields.Boolean(
        string="Lead Storage",
    )
    solartree_lead_scope = fields.Many2one(
        comodel_name="crm.lead.scope",
        string="Lead Scope",
        help="Scope of the lead"
    )
    solartree_lead_channel = fields.Many2one(
        comodel_name="crm.lead.channel",
        string="Lead Channel",
        help="Channel of the lead"
    )
    solartree_lead_technical = fields.Many2one(
        comodel_name="crm.lead.technical",
        string="Technical",
        help="Technical of the lead"
    )
    solartree_lead_structure_type = fields.Many2one(
        comodel_name="crm.lead.structure.type",
        string="Lead Structure Type",
        help="Structure Type of the lead"
    )
    solartree_lead_structure_model = fields.Many2one(
        comodel_name="crm.lead.structure.model",
        string="Lead Structure Model",
        help="Structure Model of the lead"
    )
    revision_ids = fields.One2many(
        'crm.lead.revision',
        'lead_id',
    )
    revision_count = fields.Integer(
        compute='_compute_revision_count'
    )

    def _compute_revision_count(self):
        for lead in self:
            lead.revision_count = len(lead.revision_ids)

    def action_view_revisions(self):
        """This method opens the view showing the revisions linked to the current lead."""
        self.ensure_one()
        return {
            'name': 'Revisions',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead.revision',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
            'target': 'current',
        }

    _sql_constraints = [
        ("crm_lead_unique_solartree_code", "UNIQUE (solartree_code)", _("The lead code must be unique!")),
    ]

