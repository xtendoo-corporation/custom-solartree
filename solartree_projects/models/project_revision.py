from odoo import models, fields, api


class ProjectRevision(models.Model):
    _name = 'project.revision'
    _description = 'Project Revision'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Revision Name",
        readonly=False,
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project'
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

    company_currency = fields.Many2one(
        "res.currency",
        string='Currency',
        compute="_compute_company_currency",
        compute_sudo=True
    )
    offer_class = fields.Char(
        string='Offer Class',
        compute='_compute_offer_class',
        store=True,
        readonly=True,
    )

    offer_class_id = fields.Many2one(
        'offer.class',
        string='Offer Class relation',
        compute='_compute_offer_class_id',
    )

    @api.depends('offer_kwn')
    def _compute_offer_class(self):
        for record in self:
            offer_class = self.env['offer.class'].search([
                ('min_value', '<=', record.offer_kwn),
                ('max_value', '>=', record.offer_kwn)
            ], limit=1)
            if offer_class:
                record.offer_class = offer_class.name
            else:
                record.offer_class = ''

    @api.depends('offer_kwn')
    def _compute_offer_class_id(self):
        for record in self:
            offer_class = self.env['offer.class'].search([
                ('min_value', '<=', record.offer_kwn),
                ('max_value', '>=', record.offer_kwn)
            ], limit=1)
            if offer_class:
                record.offer_class_id = offer_class
            else:
                record.offer_class_id = False

    offer_evacuation = fields.Many2one(
        comodel_name="crm.lead.evacuation",
        string="Evacuation revisions field",
    )

    revision_inverter_ids = fields.One2many(
        "project.revision.inverter",
        "revision_id",
        string="",
    )

    revision_battery_ids = fields.One2many(
        "project.revision.battery",
        "revision_id",
        string="",
    )

    revision_energy_simulation_project_production_ids = fields.One2many(
        "project.revision.energy.simulation.production",
        "revision_id",
        string="",
    )

    revision_energy_simulation_project_demand_ids = fields.One2many(
        "project.revision.energy.simulation.demand",
        "revision_id",
        string="",
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
    offer_structure_manufacturer = fields.Char(
        string="Structure Manufacturer",
    )
    offer_structure_description = fields.Char(
        string="Structure Description",
    )
    avg_price = fields.Float(
        string="Average Price",
        digits=(12, 5),
    )
    surplus_price = fields.Float(
        string="Surplus Price",
        digits=(12, 5),
    )

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

    offer_selected = fields.Boolean(
        string='Selected',
        compute='_compute_offer_selected',
    )

    @api.onchange('offer_selected')
    def _onchange_offer_selected(self):
        for record in self:
            print("*" * 80)
            print("Onchange Offer Selected", record.id)
            if record.offer_selected:
                # Deseleccionar otras revisiones
                record.lead_id.revision_ids.filtered(lambda r: r.id != record.id).write({'offer_selected': False})
                record.project_id.lead_id.selected_revision_id = record

    def _compute_offer_selected(self):
        for record in self:
            record.offer_selected = record.id == record.project_id.lead_id.selected_revision_id.id

    @api.model
    def write(self, vals):
        result = super(ProjectRevision, self).write(vals)
        if 'offer_selected' in vals and vals['offer_selected']:
            for record in self:
                # Deseleccionar otras revisiones del mismo lead_id
                record.lead_id.revision_ids.filtered(lambda r: r.id != record.id).write({'offer_selected': False})
        return result

    def copy(self, default=None):
        if default is None:
            default = {}
        lead_id = self.lead_id.id
        existing_revisions_count = self.search_count([('lead_id', '=', lead_id)])
        default['name'] = f'R{existing_revisions_count}'
        print(f"Copying revision for lead ID: {lead_id}, new name: {default['name']}")

        # Duplicate related records
        default['revision_inverter_ids'] = [(0, 0, {
            'type_inverter_id': line.type_inverter_id.id,
            'offer_inverter_model': line.offer_inverter_model,
            'offer_inverter_unit_power': line.offer_inverter_unit_power,
            'offer_inverter_quantity': line.offer_inverter_quantity,
        }) for line in self.revision_inverter_ids]
        print(f"Copied inverter records: {default['revision_inverter_ids']}")

        default['revision_battery_ids'] = [(0, 0, {
            'type_battery_id': line.type_battery_id.id,
            'offer_battery_model': line.offer_battery_model,
            'offer_battery_capacity': line.offer_battery_capacity,
            'offer_battery_power': line.offer_battery_power,
        }) for line in self.revision_battery_ids]
        print(f"Copied battery records: {default['revision_battery_ids']}")

        default['revision_energy_simulation_project_production_ids'] = [(0, 0, {
            'type_energy_simulation_project_production_id': line.type_energy_simulation_project_production_id.id,
            'total': line.total,
            'percentage': line.percentage,
        }) for line in self.revision_energy_simulation_project_production_ids]

        default['revision_energy_simulation_project_demand_ids'] = [(0, 0, {
            'type_energy_simulation_project_demand_id': line.type_energy_simulation_project_demand_id.id,
            'total': line.total,
            'percentage': line.percentage,
        }) for line in self.revision_energy_simulation_project_demand_ids]

        return super(ProjectRevision, self).copy(default)


    def unlink(self):
        for record in self:
            # Ejecutar consultas SQL para eliminar datos relacionados
            self._cr.execute("DELETE FROM project_revision_inverter WHERE revision_id = %s", (record.id,))
            self._cr.execute("DELETE FROM project_revision_battery WHERE revision_id = %s", (record.id,))
            self._cr.execute("DELETE FROM project_revision_energy_simulation_production WHERE revision_id = %s",
                             (record.id,))
            self._cr.execute("DELETE FROM project_revision_energy_simulation_demand WHERE revision_id = %s",
                             (record.id,))
        return super(ProjectRevision, self).unlink()
