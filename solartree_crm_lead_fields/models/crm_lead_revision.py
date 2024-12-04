from os import readv

from odoo import models, fields, api


class CrmLeadRevision(models.Model):
    _name = 'crm.lead.revision'
    _description = 'Lead Revision'
    _inherit = ['mail.thread', 'mail.activity.mixin']

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

    @api.depends('revision_inverter_ids.offer_inverter_quantity', 'revision_inverter_ids.offer_inverter_unit_power')
    def _compute_offer_kwn(self):
        for record in self:
            record.offer_kwn = sum(inverter.offer_inverter_quantity * inverter.offer_inverter_unit_power for inverter in
                                   record.revision_inverter_ids)

    offer_storage_kwh = fields.Float(
        string='Offer storage kWh',
        digits=(16, 1),
        compute='_compute_offer_storage_kwh',
        store=True,
    )

    @api.depends('revision_battery_ids.offer_battery_capacity', 'revision_battery_ids.offer_battery_quantity')
    def _compute_offer_storage_kwh(self):
        for record in self:
            record.offer_storage_kwh = sum(
                battery.offer_battery_capacity * battery.offer_battery_quantity for battery in
                record.revision_battery_ids)

    offer_storage_kwn = fields.Float(
        string='Offer storage kWn',
        digits=(16, 1),
        compute='_compute_offer_storage_kwn',
        store=True,
    )

    @api.depends('revision_battery_ids.offer_battery_power', 'revision_battery_ids.offer_battery_quantity')
    def _compute_offer_storage_kwn(self):
        for record in self:
            record.offer_storage_kwn = sum(
                battery.offer_battery_power * battery.offer_battery_quantity for battery in
                record.revision_battery_ids)

    offer_ve_kwn = fields.Float(
        string='Offer VE kWh',
        digits=(16, 1)
    )
    offer_tot = fields.Many2one(
        comodel_name="res.users",
        string="TOT revisions field",
    )
    offer_HT = fields.Float(
        string='Offer HT'
    )
    offer_date_deliver = fields.Date(
        string='Offer deliver date'
    )
    offer_pb_actual = fields.Float(
        string='PB actuals',
        digits=(16, 1)
    )
    offer_tir_actual = fields.Float(
        string='TIR actuals %',
        digits=(16, 1),
    )
    offer_pb_omip = fields.Float(
        string='PB OMIP',
        digits=(16, 1)
    )
    offer_tir_omip = fields.Float(
        string='TIR OMIP %',
        digits=(16, 1),
    )
    offer_pb_proyection = fields.Float(
        string='PB proyection',
        digits=(16, 1)
    )
    offer_tir_proyection = fields.Float(
        string='TIR proyection %',
        digits=(16, 1),
    )
    offer_kwh_year = fields.Integer(
        string='Offer kWh/year',
    )
    offer_self_consumption = fields.Integer(
        string='Autoconsumo (kWh/año)',
    )
    offer_surplus = fields.Integer(
        string='Excedentes (kWh/año)',
        compute='_compute_offer_surplus',
    )

    @api.depends('offer_kwh_year', 'offer_self_consumption', 'solartree_lead_modality_id')
    def _compute_offer_surplus(self):
        for record in self:
            if record.solartree_lead_modality_id.name == 'AUTOCONSUMO SIN VERTIDO':
                record.offer_surplus = 0
            else:
                record.offer_surplus = record.offer_kwh_year - record.offer_self_consumption

    offer_grid = fields.Integer(
        string='Red (kWh/año)',
        compute='_compute_offer_grid',
    )

    @api.depends('lead_id.customer_consumption_mwh', 'offer_self_consumption')
    def _compute_offer_grid(self):
        for record in self:
            if record.lead_id and record.lead_id.customer_consumption_mwh:
                record.offer_grid = record.lead_id.customer_consumption_mwh - record.offer_self_consumption
            else:
                record.offer_grid = 0

    offer_ratio_self_consumation_vs_production = fields.Float(
        string='Ratio Autoconsumo vs Producción (%)',
        compute='_compute_offer_ratio_self_consumation_vs_production',
    )

    @api.depends('offer_kwh_year', 'offer_self_consumption')
    def _compute_offer_ratio_self_consumation_vs_production(self):
        for record in self:
            if record.offer_kwh_year:
                record.offer_ratio_self_consumation_vs_production = record.offer_self_consumption / record.offer_kwh_year
            else:
                record.offer_ratio_self_consumation_vs_production = 0

    offer_ratio_surplus_vs_production = fields.Float(
        string='Ratio Excedentes vs Producción (%)',
        compute='_compute_offer_ratio_surplus_vs_production',
    )

    @api.depends('offer_kwh_year', 'offer_surplus')
    def _compute_offer_ratio_surplus_vs_production(self):
        for record in self:
            if record.offer_kwh_year:
                record.offer_ratio_surplus_vs_production = record.offer_surplus / record.offer_kwh_year
            else:
                record.offer_ratio_surplus_vs_production = 0

    offer_ratio_self_consumation_vs_demand = fields.Float(
        string='Ratio Autoconsumo vs Demanda (%)',
        compute='_compute_offer_ratio_self_consumation_vs_demand',
    )

    @api.depends('lead_id.customer_consumption_mwh', 'offer_self_consumption')
    def _compute_offer_ratio_self_consumation_vs_demand(self):
        for record in self:
            if record.lead_id and record.lead_id.customer_consumption_mwh:
                record.offer_ratio_self_consumation_vs_demand = record.offer_self_consumption / record.lead_id.customer_consumption_mwh
            else:
                record.offer_ratio_self_consumation_vs_demand = 0

    offer_ratio_grid_vs_demand = fields.Float(
        string='Ratio Excedentes vs Demanda (%)',
        compute='_compute_offer_ratio_grid_vs_demand',
    )

    @api.depends('lead_id.customer_consumption_mwh', 'offer_grid')
    def _compute_offer_ratio_grid_vs_demand(self):
        for record in self:
            if record.lead_id and record.lead_id.customer_consumption_mwh:
                record.offer_ratio_grid_vs_demand = record.offer_grid / record.lead_id.customer_consumption_mwh
            else:
                record.offer_ratio_grid_vs_demand = 0

    customer_consumption_mwh = fields.Float(
        string='Customer Consumption (MWh)',
        related='lead_id.customer_consumption_mwh',
        store=True,
        readonly=True,
    )

    company_currency = fields.Many2one(
        "res.currency",
        string='Currency',
        compute="_compute_company_currency",
        compute_sudo=True
    )
    offer_class = fields.Char(
        string='Offer Class',
        readonly=True,
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
        ondelete='cascade'
    )

    revision_direct_costs_ids = fields.One2many(
        "crm.lead.revision.direct.costs",
        "revision_id",
        string="",
        ondelete='cascade'
    )

    def action_view_direct_costs_graph(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Direct Costs Graph',
            'res_model': 'crm.lead.revision.direct.costs',
            'view_mode': 'graph,tree,form',
            'domain': [('revision_id', '=', self.id)],
            'context': dict(self.env.context, create=False)
        }

    revision_inverter_ids = fields.One2many(
        "crm.lead.revision.inverter",
        "revision_id",
        string="",
        ondelete='cascade'
    )

    revision_battery_ids = fields.One2many(
        "crm.lead.revision.battery",
        "revision_id",
        string="",
        ondelete='cascade'
    )

    revision_energy_simulation_production_ids = fields.One2many(
        "crm.lead.revision.energy.simulation.production",
        "revision_id",
        string="",
        ondelete='cascade'
    )

    revision_energy_simulation_demand_ids = fields.One2many(
        "crm.lead.revision.energy.simulation.demand",
        "revision_id",
        string="",
        ondelete='cascade'
    )

    total_revision_percentage = fields.Monetary(
        string="Total Revision Price",
        currency_field="company_currency",
        compute="_compute_total_revision_percentage",
    )

    # New fields 06/11

    avg_price = fields.Float(
        string="Average Price",
        digits=(12, 5),
    )
    surplus_price = fields.Float(
        string="Surplus Price",
        digits=(12, 5),
    )
    pb_exced_min = fields.Float(
        string="PB Exced Min",
        digits=(16, 1),
    )
    tir_exced_min = fields.Float(
        string="TIR Exced Min %",
        digits=(16, 1),
    )
    pb_battery = fields.Float(
        string="PB Battery",
        digits=(16, 1),
    )
    tir_battery = fields.Float(
        string="TIR Battery %",
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
        string="Inverter Manufacturer",
    )
    offer_battery_manufacturer = fields.Char(
        string="Battery Manufacturer",
    )
    revision_inverter_ids = fields.One2many(
        "crm.lead.revision.inverter",
        "revision_id",
        string="",
        ondelete='cascade'
    )
    offer_structure_manufacturer = fields.Char(
        string="Structure Manufacturer",
    )
    offer_structure_description = fields.Char(
        string="Structure Description",
    )
    installation_cost_price = fields.Float(
        string="Installation Cost Price",
        digits=(16, 2),
        compute="_compute_total_direct_costs",
        readonly=False,
    )

    @api.depends('revision_direct_costs_ids.price_cost', 'revision_price_ids.price')
    def _compute_total_direct_costs(self):
        for record in self:
            direct_costs_total = sum(
                cost.price_cost for cost in record.revision_direct_costs_ids
                if cost.type_direct_costs_id
            )
            fee_prices_total = sum(
                price.price for price in record.revision_price_ids
                if price.type_price_id.behavior == 'fee_and_margins' and price.type_price_id.name in ['Fee Externo',
                                                                                                      'Fee Interno']
            )
            record.installation_cost_price = direct_costs_total + fee_prices_total

    installation_cost_price_wp = fields.Float(
        string="Installation Cost €/Wp",
        digits=(16, 4),
        compute="_compute_total_direct_costs_wp",
        readonly=False,
    )

    @api.depends('revision_direct_costs_ids.price_cost_wp')
    def _compute_total_direct_costs_wp(self):
        for record in self:
            record.installation_cost_price_wp = sum(
                cost.price_cost_wp for cost in record.revision_direct_costs_ids
                if cost.type_direct_costs_id
            )

    installation_sale_price = fields.Float(
        string="Installation Sale Price",
        digits=(16, 2),
        compute="_compute_total_sale_price",
        readonly=False,
    )

    @api.depends('revision_direct_costs_ids.price_sale')
    def _compute_total_sale_price(self):
        for record in self:
            record.installation_sale_price = sum(
                cost.price_sale for cost in record.revision_direct_costs_ids
                if cost.type_direct_costs_id
            )

    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
    )

    installation_sale_price_with_tax = fields.Float(
        string="Installation Sale Price with 21% Tax",
        digits=(16, 2),
        compute="_compute_total_sale_price_with_tax",
        readonly=True,
    )

    @api.depends('installation_sale_price', 'tax_id')
    def _compute_total_sale_price_with_tax(self):
        for record in self:
            if record.tax_id:
                print("Tax ID", record.tax_id.name)
                tax_amount = record.installation_sale_price * (record.tax_id.amount / 100)
                record.installation_sale_price_with_tax = record.installation_sale_price + tax_amount
            else:
                record.installation_sale_price_with_tax = record.installation_sale_price

    installation_sale_price_wp = fields.Float(
        string="Installation Sale Price €/Wp",
        digits=(16, 4),
        compute="_compute_total_sale_price_wp",
        readonly=False,
    )

    @api.depends('revision_direct_costs_ids.price_sale_wp')
    def _compute_total_sale_price_wp(self):
        for record in self:
            record.installation_sale_price_wp = sum(
                cost.price_sale_wp for cost in record.revision_direct_costs_ids
                if cost.type_direct_costs_id
            )

    offer_fv = fields.Float(
        string="Offer FV",
        digits=(16, 2),
        compute="_compute_offer_fv",
    )

    @api.depends('revision_direct_costs_ids.price_sale', 'installation_sale_price')
    def _compute_offer_fv(self):
        for record in self:
            include_types = self.env['crm.lead.revision.global.type'].search([
                ('name', 'in', ['Batería', 'Vehículo Eléctrico (VE)'])
            ])

            record.offer_fv = record.installation_sale_price - sum(
                cost.price_sale for cost in record.revision_direct_costs_ids if
                cost.type_direct_costs_id in include_types)

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

    offer_class_id = fields.Many2one(
        'offer.class',
        string='Offer Class relation',
        compute='_compute_offer_class',
    )

    @api.depends('offer_kwn')
    def _compute_offer_class(self):
        for record in self:
            offer_class = self.env['offer.class'].search([
                ('min_value', '<=', record.offer_kwn),
                ('max_value', '>=', record.offer_kwn)
            ], limit=1)
            if offer_class:
                record.offer_class_id = offer_class
            else:
                record.offer_class_id = False

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

        sale_tax_id = self.env.company.account_sale_tax_id
        if sale_tax_id:
            defaults['tax_id'] = sale_tax_id.id

        price_types = self.env['crm.lead.revision.global.type'].search([('behavior', '=', 'fee_and_margins')])
        revision_prices = []
        for price_type in price_types:
            revision_prices.append((0, 0, {
                'type_price_id': price_type.id,
                'percentage': 0.0,
                'price': 0.0,
                'price_wp': 0.0,
            }))

        defaults['revision_price_ids'] = revision_prices

        direct_costs_types = self.env['crm.lead.revision.global.type'].search([('behavior', '=', 'direct_costs')])
        revision_direct_costs = []
        for direct_costs_type in direct_costs_types:
            revision_direct_costs.append((0, 0, {
                'type_direct_costs_id': direct_costs_type.id,
                'price_cost': 0.0,
                'price_cost_wp': 0.0,
                'price_sale': 0.0,
                'price_sale_wp': 0.0,
            }))

        defaults['revision_direct_costs_ids'] = revision_direct_costs

        inverter_types = self.env['crm.lead.revision.global.type'].search([('behavior', '=', 'inverter')])
        revision_inverter = []
        for inverter_type in inverter_types:
            revision_inverter.append((0, 0, {
                'type_inverter_id': inverter_type.id,
                'offer_inverter_model': '',
                'offer_inverter_unit_power': 0.0,
                'offer_inverter_quantity': 0,
            }))

        defaults['revision_inverter_ids'] = revision_inverter

        battery_types = self.env['crm.lead.revision.global.type'].search([('behavior', '=', 'battery')])
        revision_battery = []
        for battery_type in battery_types:
            revision_battery.append((0, 0, {
                'type_battery_id': battery_type.id,
                'offer_battery_model': '',
                'offer_battery_capacity': 0.0,
                'offer_battery_power': 0.0,
            }))

        defaults['revision_battery_ids'] = revision_battery

        energy_types_production = self.env['crm.lead.revision.global.type'].search(
            [('behavior', '=', 'energy_simulation'), ('behavior_extra', '=', 'production')])
        revision_energy_simulation_production = []
        for energy_type in energy_types_production:
            revision_energy_simulation_production.append((0, 0, {
                'type_energy_simulation_production_id': energy_type.id,
                'total': 0,
                'percentage': 0.0,
            }))

        defaults['revision_energy_simulation_production_ids'] = revision_energy_simulation_production

        energy_types_demand = self.env['crm.lead.revision.global.type'].search(
            [('behavior', '=', 'energy_simulation'),
             ('behavior_extra', '=', 'demand')])
        revision_energy_simulation_demand = []
        for energy_type in energy_types_demand:
            revision_energy_simulation_demand.append((0, 0, {
                'type_energy_simulation_demand_id': energy_type.id,
                'total': 0,
                'percentage': 0.0,
            }))

        defaults['revision_energy_simulation_demand_ids'] = revision_energy_simulation_demand

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

        # Duplicate related records
        default['revision_price_ids'] = [(0, 0, {
            'type_price_id': line.type_price_id.id,
            'percentage': line.percentage,
            'price': line.price,
            'price_wp': line.price_wp,
        }) for line in self.revision_price_ids]

        default['revision_direct_costs_ids'] = [(0, 0, {
            'type_direct_costs_id': line.type_direct_costs_id.id,
            'price_cost': line.price_cost,
            'price_cost_wp': line.price_cost_wp,
            'price_sale': line.price_sale,
            'price_sale_wp': line.price_sale_wp,
        }) for line in self.revision_direct_costs_ids]

        default['revision_inverter_ids'] = [(0, 0, {
            'type_inverter_id': line.type_inverter_id.id,
            'offer_inverter_model': line.offer_inverter_model,
            'offer_inverter_unit_power': line.offer_inverter_unit_power,
            'offer_inverter_quantity': line.offer_inverter_quantity,
        }) for line in self.revision_inverter_ids]

        default['revision_battery_ids'] = [(0, 0, {
            'type_battery_id': line.type_battery_id.id,
            'offer_battery_model': line.offer_battery_model,
            'offer_battery_capacity': line.offer_battery_capacity,
            'offer_battery_power': line.offer_battery_power,
        }) for line in self.revision_battery_ids]

        default['revision_energy_simulation_production_ids'] = [(0, 0, {
            'type_energy_simulation_production_id': line.type_energy_simulation_production_id.id,
            'total': line.total,
            'percentage': line.percentage,
        }) for line in self.revision_energy_simulation_production_ids]

        default['revision_energy_simulation_demand_ids'] = [(0, 0, {
            'type_energy_simulation_demand_id': line.type_energy_simulation_demand_id.id,
            'total': line.total,
            'percentage': line.percentage,
        }) for line in self.revision_energy_simulation_demand_ids]

        return super(CrmLeadRevision, self).copy(default)

    def unlink(self):
        for record in self:
            # Ejecutar consultas SQL para eliminar datos relacionados
            self._cr.execute("DELETE FROM crm_lead_revision_prices WHERE revision_id = %s", (record.id,))
            self._cr.execute("DELETE FROM crm_lead_revision_direct_costs WHERE revision_id = %s", (record.id,))
            self._cr.execute("DELETE FROM crm_lead_revision_inverter WHERE revision_id = %s", (record.id,))
            self._cr.execute("DELETE FROM crm_lead_revision_energy_simulation WHERE revision_id = %s", (record.id,))
            self._cr.execute("DELETE FROM crm_lead_revision_battery WHERE revision_id = %s", (record.id,))
        return super(CrmLeadRevision, self).unlink()
