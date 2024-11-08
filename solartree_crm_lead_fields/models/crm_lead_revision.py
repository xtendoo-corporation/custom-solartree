from os import readv

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
        store=True
    )
    solartree_lead_scope = fields.Many2one(
        comodel_name="crm.lead.scope",
        string="Lead Scope",
        store=True
    )
    solartree_lead_modality_id = fields.Many2one(
        comodel_name="crm.lead.modality",
        string="Lead Modality",
        store=True
    )
    solartree_lead_collective = fields.Boolean(
        string="Lead Collective",
        store=True
    )
    solartree_lead_storage = fields.Boolean(
        string="Lead Storage",
        store=True
    )
    solartree_lead_structure_type = fields.Many2one(
        comodel_name="crm.lead.structure.type",
        string="Lead Structure Type",
        store=True
    )
    solartree_lead_structure_model = fields.Many2one(
        comodel_name="crm.lead.structure.model",
        string="Lead Structure Model",
        store=True
    )
    offer_kwp = fields.Float(
        string='Offer kWp',
        compute='_compute_offer_kwp',
        store=True,
        readonly=False,
    )

    @api.depends('offer_modules_quantity', 'offer_modules_unit_power')
    def _compute_offer_kwp(self):
        for record in self:
            if record.offer_modules_unit_power:
                record.offer_kwp = record.offer_modules_quantity * (record.offer_modules_unit_power / 1000)
            else:
                record.offer_kwp = 0.0

    offer_kwn = fields.Float(
        string='Offer kWn',
        digits=(16, 1),
        compute='_compute_offer_kwn',
        store=True,
        readonly=False,
    )

    @api.depends('offer_inverter_1_quantity', 'offer_inverter_1_unit_power', 'offer_inverter_2_quantity',
                 'offer_inverter_2_unit_power')
    def _compute_offer_kwn(self):
        for record in self:
            record.offer_kwn = record.offer_inverter_1_quantity * record.offer_inverter_1_unit_power + (
                        record.offer_inverter_2_quantity * record.offer_inverter_2_unit_power)


    offer_storage_kwh = fields.Float(
        string='Offer storage kWh',
        digits=(16, 1)
    )
    offer_storage_kwn = fields.Float(
        string='Offer storage kWn',
        digits=(16, 1)
    )
    offer_ve_kwn = fields.Float(
        string='Offer VE kWh',
        digits=(16, 1)
    )
    offer_tot = fields.Many2one(
        comodel_name="crm.lead.tot",
        string="TOT revisions field",
    )
    offer_HT = fields.Float(
        string='Offer HT'
    )
    offer_date_deliver = fields.Date(
        string='Offer deliver date'
    )
    fee_mbsv = fields.Float(
        string='Fee MBSV',
        readonly=True,
        compute="_compute_fee_mbsv",
    )

    @api.depends('total_revision_percentage')
    def _compute_fee_mbsv(self):
        for record in self:
            record.fee_mbsv = record.total_revision_percentage

    fee_mbsv_price = fields.Monetary(
        string='Fee MBSV Price',
        currency_field='company_currency',
        compute="_compute_fee_mbsv_price",
    )

    @api.depends('fee_mbsv', 'offer_price_rx')
    def _compute_fee_mbsv_price(self):
        for record in self:
            record.fee_mbsv_price = record.offer_price_rx * record.fee_mbsv

    fee_mbsv_price_wp = fields.Monetary(
        string='Fee MBSV Price WP',
        currency_field='company_currency',
        compute="_compute_fee_mbsv_price_wp",
    )

    @api.depends('fee_mbsv_price', 'offer_kwp')
    def _compute_fee_mbsv_price_wp(self):
        for record in self:
            if record.offer_kwp:
                record.fee_mbsv_price_wp = record.fee_mbsv_price / (record.offer_kwp * 1000)
            else:
                record.fee_mbsv_price_wp = 0.0

    fee_cost_price = fields.Monetary(
        string='Fee Cost Price',
        currency_field='company_currency',
        compute="_compute_fee_cost_price",
    )

    @api.depends('fee_mbsv_price', 'offer_price_rx')
    def _compute_fee_cost_price(self):
        for record in self:
            record.fee_cost_price = record.offer_price_rx - record.fee_mbsv_price

    fee_cost_price_wp = fields.Monetary(
        string='Fee Cost Price WP',
        currency_field='company_currency',
        compute="_compute_fee_cost_price_wp",
    )

    @api.depends('fee_cost_price', 'offer_kwp')
    def _compute_fee_cost_price_wp(self):
        for record in self:
            if record.offer_kwp:
                record.fee_cost_price_wp = record.fee_cost_price / (record.offer_kwp * 1000)
            else:
                record.fee_cost_price_wp = 0.0

    offer_wp = fields.Float(
        string='Offer €/Wp',
        readonly=True,
        compute="_compute_wp",
        digits=(12, 4),
    )
    offer_pb_actual = fields.Float(
        string='PB actuals',
        digits=(16, 1)
    )
    offer_tir_actual = fields.Float(
        string='TIR actuals',
        digits = (16, 2),
    )
    offer_pb_omip = fields.Float(
        string='PB OMIP',
        digits=(16, 2)
    )
    offer_tir_omip = fields.Float(
        string='TIR OMIP',
        digits=(16, 2),
    )
    offer_pb_proyection = fields.Float(
        string='PB proyection',
        digits=(16, 1)
    )
    offer_tir_proyection = fields.Float(
        string='TIR proyection',
        digits = (16, 1),
    )
    offer_kwh_year = fields.Integer(
        string='Offer kWh/year',
    )
    company_currency = fields.Many2one(
        "res.currency",
        string='Currency',
        compute="_compute_company_currency",
        compute_sudo=True
    )
    offer_price_rx = fields.Float(
        string='Offer Total Price',
        compute='_compute_offer_price_rx',
        store=True
    )

    @api.depends('revision_total_price_ids.price')
    def _compute_offer_price_rx(self):
        for record in self:
            if record.revision_total_price_ids:
                record.offer_price_rx = sum(record.revision_total_price_ids.mapped('price'))
                print("Offer Price RX 1", record.offer_price_rx)
            else:
                record.offer_price_rx = 0.0
                print("Offer Price RX 2", record.offer_price_rx)

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
        string="",
    )

    revision_total_price_ids = fields.One2many(
        "crm.lead.revision.total.price.rx",
        "revision_id",
        string="",
    )
    total_revision_percentage = fields.Monetary(
        string="Total Revision Price",
        currency_field="company_currency",
        compute="_compute_total_revision_percentage",
    )

    # New fields 06/11

    avg_price = fields.Float(
        string="Average Price",
        digits=(12, 4),
    )
    surplus_price = fields.Float(
        string="Surplus Price",
        digits=(12, 4),
    )
    pb_exced_min = fields.Float(
        string="PB Exced Min",
        digits=(16, 1),
    )
    tir_exced_min = fields.Float(
        string="TIR Exced Min",
        digits=(16, 1),
    )
    offer_fabricant_modules = fields.Char(
        string="Fabricant Modules",
    )
    offer_modules_model = fields.Char(
        string="Modules Model",
    )
    offer_modules_unit_power = fields.Integer(
        string="Modules Unit Power",
    )
    offer_modules_quantity = fields.Integer(
        string="Modules Quantity",
    )
    offer_inverter_manufacturer = fields.Char(
        string="Investor Manufacturer",
    )
    offer_inverter_1_model = fields.Char(
        string="Investor 1 Model",
    )
    offer_inverter_1_unit_power = fields.Float(
        string="Investor 1 Unit Power",
        digits=(16, 1),
    )
    offer_inverter_1_quantity = fields.Integer(
        string="Investor 1 Quantity",
    )
    offer_inverter_2_model = fields.Char(
        string="Investor 2 Model",
    )
    offer_inverter_2_unit_power = fields.Float(
        string="Investor 2 Unit Power",
        digits=(16, 1),
    )
    offer_inverter_2_quantity = fields.Integer(
        string="Investor 2 Quantity",
    )
    offer_structure_manufacturer = fields.Char(
        string="Structure Manufacturer",
    )
    offer_structure_description = fields.Char(
        string="Structure Description",
    )



    @api.depends('revision_price_ids.percentage')
    def _compute_total_revision_percentage(self):
        for record in self:
            record.total_revision_percentage = sum(record.revision_price_ids.mapped('percentage'))

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


    @api.depends('revision_total_price_ids.price', 'offer_kwp')
    def _compute_wp(self):
        for record in self:
            fv_price_type = self.env['crm.lead.revision.total.price.rx.type'].search([('name', '=', 'FV')],
                                                                                     limit=1)
            if fv_price_type:
                fv_price_record = record.revision_total_price_ids.filtered(
                    lambda r: r.type_total_price_id == fv_price_type)
                if fv_price_record and record.offer_kwp:
                    record.offer_wp = round(fv_price_record.price / (record.offer_kwp * 1000), 4)
                else:
                    record.offer_wp = 0.0
            else:
                record.offer_wp = 0.0

    @api.depends('lead_id.company_id')
    def _compute_company_currency(self):
        for record in self:
            if record.lead_id and record.lead_id.company_id:
                record.company_currency = record.lead_id.company_id.currency_id or self.env.company.currency_id
            else:
                record.company_currency = self.env.company.currency_id

            print("Record ID %s, Currency Set to %s", record.id, record.company_currency)

    @api.model
    def default_get(self, fields_list):
        defaults = super(CrmLeadRevision, self).default_get(fields_list)
        lead_id = self.env.context.get('default_lead_id')
        if lead_id:
            existing_revisions_count = self.search_count([('lead_id', '=', lead_id)])
            defaults['name'] = f'R{existing_revisions_count}'
            print(f"LEAD ID encontrado: {lead_id}")
            print(f"Nombre de la revisión asignado: {defaults['name']}")
        else:
            print("LEAD ID no encontrado en el contexto")
        price_types = self.env['crm.lead.revision.price.type'].search([])
        revision_prices = []
        for price_type in price_types:
            revision_prices.append((0, 0, {
                'type_price_id': price_type.id,
                'percentage': 0.0,
                'price': 0.0,
                'price_wp': 0.0,
            }))

        defaults['revision_price_ids'] = revision_prices

        total_price_types = self.env['crm.lead.revision.total.price.rx.type'].search([])
        revision_total_prices = []
        for total_price_type in total_price_types:
            revision_total_prices.append((0, 0, {
                'type_total_price_id': total_price_type.id,
                'price': 0.0,

            }))

        defaults['revision_total_price_ids'] = revision_total_prices
        return defaults

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

    def copy(self, default=None):
        if default is None:
            default = {}
        lead_id = self.lead_id.id
        existing_revisions_count = self.search_count([('lead_id', '=', lead_id)])
        default['name'] = f'R{existing_revisions_count}'
        return super(CrmLeadRevision, self).copy(default)
