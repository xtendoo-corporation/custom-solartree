from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class CrmLead(models.Model):
    _inherit = ["crm.lead"]

    solartree_code = fields.Char(
        string="Lead Code",
        required=True,
        copy=False
    )
    # solartree_lead_type_id = fields.Many2one(
    #     comodel_name="crm.lead.type",
    #     string="Lead Type",
    #     required=True,
    #     help="Type of the lead"
    # )
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
    )
    solartree_date_request = fields.Date(
        string="Date Request",
    )
    solartree_date_required_delivery = fields.Date(
        string="Date Required Delivery",
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
        domain="[('lead_id', '=', id)]",
    )
    #Campos nuevos a partir de 04/11/24
    design_notes = fields.Text(
        string="Observaciones Diseño",
        help="Notas relacionadas con el diseño."
    )
    customer_consumption_mwh = fields.Float(
        string="Customer Consumption (MWh/year)",
        digits=(16, 0),
        help="Annual customer energy consumption in MWh."
    )
    max_power_bie = fields.Float(
        string="Max Power BIE (kW)",
        digits=(16, 2),
        help="Maximum BIE power in kW."
    )
    lead_fee = fields.Many2one(
        comodel_name="crm.lead.fee",
        string="Lead Fee Model",
        help="Fee Model of the lead"
    )
    lead_tension_level = fields.Many2one(
        comodel_name="crm.lead.tension.level",
        string="Lead Tension Level Model",
        help="Tension Level Model of the lead"
    )
    partner_address_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner Address',
        domain="[('parent_id', '=', 'partner_id')]"
    )
    expected_revenue = fields.Monetary(
        string='Expected Revenue',
        currency_field='company_currency',
        tracking=True,
        compute='_compute_expected_revenue',
        store=True
    )
    extension_rights = fields.Float(
        string="Extension Rights (kW)",
        digits=(16, 2),
    )
    access_rights = fields.Float(
        string="Access Rights (kW)",
        digits=(16, 2),
    )
    #FIELDS TO VIEW IN KANBAN VIEW
    offer_kwp = fields.Float(
        related='selected_revision_id.offer_kwp',
        string='Offer kWp',
        readonly=False
    )
    offer_price_rx = fields.Float(
        related='selected_revision_id.offer_price_rx',
        string='Offer Price RX',
        readonly=False
    )
    offer_wp = fields.Float(
        related='selected_revision_id.offer_wp',
        string='Offer WP',
        readonly=False
    )
    solartree_lead_type_id = fields.Many2one(
        related='selected_revision_id.solartree_lead_type_id',
        comodel_name='crm.lead.type',
        string='Lead Type',
        readonly=False
    )

    offer_class = fields.Char(
        string='Offer Class',
        related='selected_revision_id.offer_class',
        store=True,
        readonly=True
    )

    @api.depends('selected_revision_id.offer_price_rx')
    def _compute_expected_revenue(self):
        for lead in self:
            lead.expected_revenue = lead.selected_revision_id.offer_price_rx if lead.selected_revision_id else 0.0

    @api.onchange('selected_revision_id')
    def _onchange_selected_revision_id(self):
        for record in self:
            if record.selected_revision_id:
                record.solartree_date_required_delivery = record.selected_revision_id.offer_date_deliver

    @api.depends('revision_ids.offer_selected')
    def _compute_selected_revision_id(self):
        print("?" * 80)
        print("_compute_selected_revision_id")
        for record in self:
            selected_revision = record.revision_ids.filtered(lambda r: r.offer_selected)
            record.selected_revision_id = selected_revision[:1]

    @api.onchange('revision_ids')
    def _onchange_revision_ids(self):
        print("-" * 80)
        print("Onchange Revision IDs")
        for record in self:
            offer_selected_revisions = record.revision_ids.filtered(lambda r: r.offer_selected)
            if offer_selected_revisions:
                record.selected_revision_id = offer_selected_revisions[0]
            else:
                record.selected_revision_id = False

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


    def _address_as_string(self):
        self.ensure_one()
        addr = []
        if self.partner_address_id:
            if self.partner_address_id.street:
                addr.append(self.partner_address_id.street)
            if self.partner_address_id.street2:
                addr.append(self.partner_address_id.street2)
            if hasattr(self.partner_address_id, "street3") and self.partner_address_id.street3:
                addr.append(self.partner_address_id.street3)
            if self.partner_address_id.city:
                addr.append(self.partner_address_id.city)
            if self.partner_address_id.state_id:
                addr.append(self.partner_address_id.state_id.name)
            if self.partner_address_id.country_id:
                addr.append(self.partner_address_id.country_id.name)
        if not addr:
            raise UserError(_("Address missing on partner address '%s'.") % self.partner_address_id.name)
        return " ".join(addr)

    @api.model
    def _prepare_url(self, url, replace):
        assert url, "Missing URL"
        for key, value in replace.items():
            if not isinstance(value, str):
                if isinstance(value, float):
                    value = "%.5f" % value
                else:
                    value = ""
            url = url.replace(key, value)
        return url

    def open_map(self):
        self.ensure_one()
        map_website = self.env.user.context_map_website_id
        if not map_website:
            raise UserError(
                _("Missing map provider: you should set it in your preferences.")
            )
        if map_website.lat_lon_url and self.partner_address_id.partner_latitude and self.partner_address_id.partner_longitude:
            url = self._prepare_url(
                map_website.lat_lon_url,
                {
                    "{LATITUDE}": self.partner_address_id.partner_latitude,
                    "{LONGITUDE}": self.partner_address_id.partner_longitude,
                },
            )
        else:
            if not map_website.address_url:
                raise UserError(
                    _("Missing parameter 'URL that uses the address' for map website '%s'.") % map_website.name
                )
            url = self._prepare_url(
                map_website.address_url, {"{ADDRESS}": self._address_as_string()}
            )
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    @api.constrains('type', 'solartree_lead_channel', 'solartree_lead_identification', 'solartree_date_request')
    def _check_required_fields_for_opportunity(self):
        for record in self:
            if record.type == 'opportunity':
                if not record.solartree_lead_channel or not record.solartree_lead_identification or not record.solartree_date_request:
                    raise ValidationError(
                        _("The fields 'Lead Channel', 'Lead Identification', and 'Date Request' must be filled when the type is 'opportunity'."))
