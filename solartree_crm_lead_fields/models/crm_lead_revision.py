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

    @api.onchange('offer_selected')
    def _onchange_offer_selected(self):
        for record in self:
            print("*"*80)
            print("Onchange Offer Selected", record.id)
            record.lead_id.selected_revision_id.id = record.id

    def _compute_offer_selected(self):
        print("/"*80)
        print("_compute_offer_selected")

        # self.lead_id.selected_revision_id.id = self.id

        for record in self:

            print("Compute offer selected", record.id)
            print("Lead ID", record.lead_id)
            print("Selected Revision ID", record.lead_id.selected_revision_id)
            print("record.id == record.lead_id.selected_revision_id.id", record.id == record.lead_id.selected_revision_id.id)

            record.offer_selected = (record.id == record.lead_id.selected_revision_id.id)

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
    def create(self, vals):
        print("Valores recibidos: ", vals)
        lead_id = vals.get('lead_id') or self.env.context.get('default_lead_id')

        if lead_id:
            existing_revisions_count = self.search_count([('lead_id', '=', lead_id)])
            vals['name'] = f'R{existing_revisions_count}'
            print("LEAD ID encontrado: " + str(lead_id))
            print("Nombre de la revisión asignado: " + vals['name'])

        else:
            print("LEAD ID no encontrado en los valores o contexto")

        return super(CrmLeadRevision, self).create(vals)

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
