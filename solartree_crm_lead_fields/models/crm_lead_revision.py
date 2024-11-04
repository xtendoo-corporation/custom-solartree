from odoo import models, fields, api


class CrmLeadRevision(models.Model):
    _name = 'crm.lead.revision'
    _description = 'Lead Revision'

    name = fields.Char(
        string="Revision Name",
        readonly=False,
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string="Opportunity",
        required=True,
        ondelete='cascade'
    )
    solartree_lead_type_id = fields.Many2one(
        comodel_name="crm.lead.type",
        string="Lead Type",
        related="lead_id.solartree_lead_type_id",
        readonly=True,
        store=True
    )
    solartree_lead_scope = fields.Many2one(
        comodel_name="crm.lead.scope",
        string="Lead Scope",
        related="lead_id.solartree_lead_scope",
        readonly=True,
        store=True
    )
    solartree_lead_modality_id = fields.Many2one(
        comodel_name="crm.lead.modality",
        string="Lead Modality",
        related="lead_id.solartree_lead_modality_id",
        readonly=True,
        store=True
    )
    solartree_lead_collective = fields.Boolean(
        string="Lead Collective",
        related="lead_id.solartree_lead_collective",
        readonly=True,
        store=True
    )
    solartree_lead_storage = fields.Boolean(
        string="Lead Storage",
        related="lead_id.solartree_lead_storage",
        readonly=True,
        store=True
    )
    solartree_lead_structure_type = fields.Many2one(
        comodel_name="crm.lead.structure.type",
        string="Lead Structure Type",
        related="lead_id.solartree_lead_structure_type",
        readonly=True,
        store=True
    )
    solartree_lead_structure_model = fields.Many2one(
        comodel_name="crm.lead.structure.model",
        string="Lead Structure Model",
        related="lead_id.solartree_lead_structure_model",
        readonly=True,
        store=True
    )
    offer_kwp = fields.Float(
        'Offer kWp'
    )
    offer_kwn = fields.Float(
        'Offer kWn',
        digits=(16, 1)
    )
    offer_storage_kwh = fields.Float(
        'Offer storage kWh',
        digits=(16, 1)
    )
    offer_storage_kwn = fields.Float(
        'Offer storage kWn',
        digits=(16, 1)
    )
    offer_ve_kwn = fields.Float(
        'Offer VE kWh',
        digits=(16, 1)
    )
    offer_tot = fields.Many2one(
        comodel_name="crm.lead.tot",
        string="TOT revisions field",
    )
    offer_HT = fields.Float(
        'Offer HT'
    )
    offer_date_deliver = fields.Date(
        'Offer deliver date'
    )
    offer_fee_external = fields.Float(
        'Offer fee external'
    )
    offer_fee_internal = fields.Float(
        'Offer fee internal'
    )
    offer_gg = fields.Float(
        'Offer GG'
    )
    offer_bi = fields.Float(
        'Offer BI'
    )
    offer_mbsv = fields.Float(
        'Offer MBSV',
        readonly=True,
        compute="_compute_mbsv",
    )
    offer_fv_price = fields.Monetary(
        'Offer FV price',
        currency_field='company_currency',
    )
    offer_wp = fields.Float(
        'Offer €/Wp',
        readonly=True,
        compute="_compute_wp",
        digits=(12, 4),
    )
    offer_pb_actual = fields.Float(
        'PB actuals',
        digits=(16, 1)
    )
    offer_tir_actual = fields.Integer(
        'TIR actuals'
    )
    offer_pb_omip = fields.Float(
        'PB OMIP',
        digits=(16, 1)
    )
    offer_tir_omip = fields.Integer(
        'TIR OMIP'
    )
    offer_pb_proyection = fields.Float(
        'PB proyection',
        digits=(16, 1)
    )
    offer_tir_proyection = fields.Integer(
        'TIR proyection'
    )
    offer_storage_price = fields.Monetary(
        'Offer storage price',
        currency_field='company_currency',
    )
    offer_ve_price = fields.Monetary(
        'Offer VE Price',
        currency_field='company_currency',
    )
    offer_kwh_year = fields.Integer(
        'Offer kWh/year',
    )
    company_currency = fields.Many2one(
        "res.currency",
        string='Currency',
        compute="_compute_company_currency",
        compute_sudo=True
    )
    offer_price_rx = fields.Monetary(
        string='Offer Total Price',
        currency_field='company_currency',
        compute='_compute_offer_price_rx',
        store=True
    )
    offer_class = fields.Char(
        string='Offer Class',
        readonly=True,
        compute='_compute_offer_class',
    )
    offer_selected = fields.Boolean(
        string='Selected',
        compute='_compute_offer_selected',
    )
    offer_evacuation = fields.Many2one(
        comodel_name="crm.lead.evacuation",
        string="Evacuation revisions field",
    )

    revision_price_ids = fields.One2many(
        "crm.lead.revision.prices",
        "revision_id",
        string="Revision Prices"
    )

    offer_autoconsumo_directo_kwh = fields.Float(
        string='Oferta Autoconsumo Directo (kWh/año)',
        digits=(16, 0)
    )
    offer_avg_price_per_kwh = fields.Float(
        string='Precio medio (€/kWh)',
        digits=(12, 4)
    )
    offer_excess_price_per_kwh = fields.Float(
        string='Precio excedentes (€/kWh)',
        digits=(12, 4)
    )
    offer_autarky_fee_percentage = fields.Float(
        string='Cuota autárquica (%)',
        compute='_compute_autarky_fee_percentage',
        digits=(12, 1)
    )
    offer_pb_exced_min = fields.Float(
        string='PB Exced. Min',
        digits=(16, 1)
    )
    offer_tir_exced_min = fields.Float(
        string='TIR Exced. Min',
        digits=(16, 1)
    )
    offer_modules_manufacturer = fields.Text(
        string='Oferta Módulos Fabricante'
    )
    offer_modules_model = fields.Text(
        string='Oferta Módulos Modelo'
    )
    offer_modules_power_unit = fields.Integer(
        string='Oferta Módulos Potencia Unitaria (Wp)'
    )
    offer_modules_quantity = fields.Integer(
        string='Oferta Módulos Cantidad'
    )

    @api.depends('offer_fee_external', 'offer_price_rx')
    def _compute_offer_fee_external_euro(self):
        for record in self:
            record.offer_fee_external_euro = record.offer_fee_external * record.offer_price_rx if record.offer_price_rx else 0.0

    @api.depends('offer_fee_external_euro', 'offer_kwp')
    def _compute_offer_fee_external_per_kwp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_fee_external_per_kWp = record.offer_fee_external_euro / (record.offer_kwp * 1000)
            else:
                record.offer_fee_external_per_kWp = 0.0

    @api.depends('offer_fee_internal', 'offer_price_rx')
    def _compute_offer_fee_internal_euro(self):
        for record in self:
            record.offer_fee_internal_euro = record.offer_fee_internal * record.offer_price_rx if record.offer_price_rx else 0.0

    @api.depends('offer_fee_internal_euro', 'offer_kwp')
    def _compute_offer_fee_internal_per_kwp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_fee_internal_per_kWp = record.offer_fee_internal_euro / (record.offer_kwp * 1000)
            else:
                record.offer_fee_internal_per_kWp = 0.0

    @api.depends('offer_gg', 'offer_price_rx')
    def _compute_offer_fee_gg_euro(self):
        for record in self:
            record.offer_fee_gg_euro = record.offer_gg * record.offer_price_rx if record.offer_price_rx else 0.0

    @api.depends('offer_fee_gg_euro', 'offer_kwp')
    def _compute_offer_fee_gg_per_kwp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_fee_gg_per_kWp = record.offer_fee_gg_euro / (record.offer_kwp * 1000)
            else:
                record.offer_fee_gg_per_kWp = 0.0

    @api.depends('offer_bi', 'offer_price_rx')
    def _compute_offer_fee_bi_euro(self):
        for record in self:
            record.offer_fee_bi_euro = record.offer_bi * record.offer_price_rx if record.offer_price_rx else 0.0

    @api.depends('offer_fee_bi_euro', 'offer_kwp')
    def _compute_offer_fee_bi_per_kwp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_fee_bi_per_kWp = record.offer_fee_bi_euro / (record.offer_kwp * 1000)
            else:
                record.offer_fee_bi_per_kWp = 0.0

    @api.depends('offer_mbsv', 'offer_price_rx')
    def _compute_offer_fee_mbsv_euro(self):
        for record in self:
            record.offer_fee_mbsv_euro = record.offer_mbsv * record.offer_price_rx if record.offer_price_rx else 0.0

    @api.depends('offer_fee_mbsv_euro', 'offer_kwp')
    def _compute_offer_fee_mbsv_per_kwp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_fee_mbsv_per_kWp = record.offer_fee_mbsv_euro / (record.offer_kwp * 1000)
            else:
                record.offer_fee_mbsv_per_kWp = 0.0

    @api.depends('offer_price_rx', 'offer_fee_mbsv_euro')
    def _compute_offer_cost_euro(self):
        for record in self:
            record.offer_cost_euro = record.offer_price_rx - record.offer_fee_mbsv_euro if record.offer_price_rx else 0.0

    @api.depends('offer_cost_euro', 'offer_kwp')
    def _compute_offer_cost_per_kwp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_cost_per_kWp = record.offer_cost_euro / (record.offer_kwp * 1000)
            else:
                record.offer_cost_per_kWp = 0.0








    @api.depends('offer_kwh_year', 'lead_id.customer_consumption_mwh')
    def _compute_autarky_fee_percentage(self):
        for record in self:
            if record.lead_id.customer_consumption_mwh:
                record.offer_autarky_fee_percentage = (record.offer_kwh_year / (
                        1000 * record.lead_id.customer_consumption_mwh)) * 100
            else:
                record.offer_autarky_fee_percentage = 0.0

    @api.onchange('offer_selected')
    def _onchange_offer_selected(self):
        for record in self:
            print("*" * 80)
            print("Onchange Offer Selected", record.id)
            if record.offer_selected:
                # Deseleccionar otras revisiones
                record.lead_id.revision_ids.filtered(lambda r: r.id != record.id).write({'offer_selected': False})
                record.lead_id.selected_revision_id = record

    def _compute_offer_selected(self):
        for record in self:
            record.offer_selected = record.id == record.lead_id.selected_revision_id.id

    @api.model
    def write(self, vals):
        result = super(CrmLeadRevision, self).write(vals)
        if 'offer_selected' in vals and vals['offer_selected']:
            for record in self:
                # Deseleccionar otras revisiones del mismo lead_id
                record.lead_id.revision_ids.filtered(lambda r: r.id != record.id).write({'offer_selected': False})
        return result

    @api.depends('offer_kwn')
    def _compute_offer_class(self):
        for record in self:
            if record.offer_kwn > 1000:
                record.offer_class = "Mayor 1 MW"
            if 1000 >= record.offer_kwn > 100:
                record.offer_class = "INDUSTRIAL"
            if 100 >= record.offer_kwn > 10:
                record.offer_class = "COMERCIAL"
            if record.offer_kwn <= 10:
                record.offer_class = "PEQUEÑA INSTALACIÓN"

    @api.depends('offer_fv_price', 'offer_storage_price', 'offer_ve_price')
    def _compute_offer_price_rx(self):
        for record in self:
            record.offer_price_rx = (record.offer_fv_price or 0.0) + \
                                    (record.offer_storage_price or 0.0) + \
                                    (record.offer_ve_price or 0.0)

    @api.depends('offer_fv_price', 'offer_kwp', )
    def _compute_wp(self):
        for record in self:
            if record.offer_kwp:
                record.offer_wp = round(record.offer_fv_price / (record.offer_kwp * 1000), 4)
            else:
                record.offer_wp = 0.0

    @api.depends('offer_fee_external', 'offer_fee_internal', 'offer_gg', 'offer_bi')
    def _compute_mbsv(self):
        for record in self:
            external = record.offer_fee_external or 0.0
            internal = record.offer_fee_internal or 0.0
            gg = record.offer_gg or 0.0
            bi = record.offer_bi or 0.0

            record.offer_mbsv = external + internal + gg + bi

    @api.depends('lead_id.company_id')
    def _compute_company_currency(self):
        for record in self:
            if record.lead_id and record.lead_id.company_id:
                record.company_currency = record.lead_id.company_id.currency_id or self.env.company.currency_id
            else:
                record.company_currency = self.env.company.currency_id

            print("Record ID %s, Currency Set to %s", record.id, record.company_currency)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            lead_id = vals.get('lead_id') or self.env.context.get('default_lead_id')

            if lead_id:
                existing_revisions_count = self.search_count([('lead_id', '=', lead_id)])
                vals['name'] = f'R{existing_revisions_count}'
                print(f"LEAD ID encontrado: {lead_id}")
                print(f"Nombre de la revisión asignado: {vals['name']}")
            else:
                print("LEAD ID no encontrado en los valores o contexto")

        return super(CrmLeadRevision, self).create(vals_list)

    def action_open_revision_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Revision',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.lead.revision',
            'res_id': self.id,
            'target': 'current',
        }
