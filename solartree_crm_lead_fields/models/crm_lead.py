from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = ["crm.lead"]

    solartree_code = fields.Char(
        string="Lead Code",
        required=True,
        readonly=True,
        copy=False
    )
    solartree_lead_type_id = fields.Many2one(
        comodel_name="crm.lead.type",
        string="Lead Type",
        required=True,
        help="Type of the lead"
    )
    solartree_lead_modality_id = fields.Many2one(
        comodel_name="crm.lead.modality",
        string="Lead Modality",
        required=True,
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
        required=True,
        help="Scope of the lead"
    )
    solartree_lead_channel = fields.Many2one(
        comodel_name="crm.lead.channel",
        string="Lead Channel",
        required=True,
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
        required=True,
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
    solartree_lead_identification = fields.Char(
        string="Lead Identification",
        required=True,
    )
    solartree_date_request = fields.Date(
        string="Date Request",
        required=True,
    )
    solartree_date_required_delivery = fields.Date(
        string="Date Required Delivery",
        required=True,
    )
    solartree_additional_deliverables = fields.Char(
        string="Additional Deliverables",
    )
    solartree_connection_point_location = fields.Char(
        string="Connection Point Location",
    )
    solartree_specific_comments = fields.Char(
        string="Specific Comments"
    )
    solartree_offer_ht = fields.Float(
        string="Total Offer HT",
        compute="_compute_solartree_offer_ht",
        store=True,
    )
    solartree_cups = fields.Char(
        string="CUPS",
        size=22,
    )
    solartree_date_proposed_signature = fields.Date(
        string="Date Proposed Signature",
    )
    solartree_date_kom = fields.Date(
        string="Date KOM",
    )
    solartree_date_visit = fields.Date(
        string="Date Visit",
    )
    solartree_date_deliverables = fields.Date(
        string="Date Deliverables",
    )
    solartree_date_sign_contract = fields.Date(
        string="Date Sign Contract",
    )
    solartree_num_proyect = fields.Char(
        string="Nº Proyect"
    )
    selected_revision_id = fields.Many2one(
        'crm.lead.revision',
        string="Selected Revision",
    )

    @api.depends('revision_ids.offer_selected')
    def _compute_selected_revision_id(self):
        print("?" * 80)
        print("_compute_selected_revision_id")
        for record in self:
            selected_revision = record.revision_ids.filtered(lambda r: r.offer_selected)
            record.selected_revision_id = selected_revision

    @api.onchange('revision_ids')
    def _onchange_revision_ids(self):
        print("-" * 80)
        print("Onchange Revision IDs")

        for record in self:
            offer_selected_revisions = record.revision_ids.filtered(lambda r: r.offer_selected)

            print("Onchange Revision IDs", offer_selected_revisions[0].name)

            if offer_selected_revisions:
                record.selected_revision_id = offer_selected_revisions[0]

    @api.constrains('solartree_cups')
    def _check_cups_length(self):
        for record in self:
            if record.solartree_cups and len(record.solartree_cups) not in [20, 22]:
                raise ValidationError("El campo 'CUPS' debe tener 20 o 22 caracteres.")

    @api.depends('revision_ids.offer_HT')
    def _compute_solartree_offer_ht(self):
        for lead in self:
            total_ht = sum(revision.offer_HT for revision in lead.revision_ids)
            lead.solartree_offer_ht = total_ht

    def _compute_revision_count(self):
        for lead in self:
            lead.revision_count = len(lead.revision_ids)

    def action_view_revisions(self):
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

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env.ref("solartree_crm_lead_fields.sequence_lead", raise_if_not_found=False)
        current_year_suffix = datetime.now().year % 100

        for vals in vals_list:
            if not vals.get("solartree_code") or vals["solartree_code"] == "/":
                if sequence:
                    sequence_number = sequence.next_by_id()
                    vals["solartree_code"] = f"OF-{current_year_suffix:02d}-{sequence_number}"
                else:
                    vals["solartree_code"] = "OF-XX-XXXX"
        return super().create(vals_list)

