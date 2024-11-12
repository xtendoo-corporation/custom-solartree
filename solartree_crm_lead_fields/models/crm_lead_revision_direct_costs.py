from odoo import fields, models, api


class CrmLeadRevisionDirectCosts(models.Model):
    _name = "crm.lead.revision.direct.costs"
    _description = "Lead Revision Direct Costs"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_direct_costs_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string = "Type",
        domain = lambda self: self._domain_type_price_id(),
    )

    type_direct_costs_name = fields.Char(
        string="Type Name",
        related="type_direct_costs_id.name",
        store=True,
    )

    selected_type_price_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_price_ids',
        store=False
    )

    @api.depends('revision_id.revision_direct_costs_ids.type_direct_costs_id')
    def _compute_selected_type_price_ids(self):
        for record in self:
            record.selected_type_price_ids = record.mapped('revision_id.revision_direct_costs_ids.type_direct_costs_id')

    def _domain_type_price_id(self):
        return [('id', 'not in', self.selected_type_price_ids.ids),
                ('behavior', '=', 'direct_costs')
                ]

    price_cost = fields.Monetary(
        string="Cost",
        currency_field="company_currency",
        compute="_compute_price_cost",
        digits=(16, 2),
        store=True
    )

    @api.depends('revision_id.revision_direct_costs_ids','revision_id.revision_price_ids')
    def _compute_price_cost(self):
        for record in self:
            if record.type_direct_costs_id.name == 'BOP':
                direct_costs = record.revision_id.revision_direct_costs_ids.filtered(
                    lambda r: r.type_direct_costs_id.name in ['Modules', 'Inverter', 'Batery', 'Structure',
                                                              'Evacuation', 'H&S']
                )
                total_direct_costs = sum(direct_cost.price_cost for direct_cost in direct_costs)
                record.price_cost = record.revision_id.fee_cost_price - total_direct_costs
            elif record.type_direct_costs_id.name == 'Fee Cost':
                fee_costs = record.revision_id.revision_price_ids.filtered(
                    lambda r: r.type_price_id.name in ['Fee Externo', 'Fee Interno']
                )
                record.price_cost = sum(fee_cost.price for fee_cost in fee_costs)
            elif record.type_direct_costs_id.name == 'MBSV Solartree':
                fee_costs = record.revision_id.revision_price_ids.filtered(
                    lambda r: r.type_price_id.name in ['Gastos de estructura', 'Beneficio Industrial']
                )
                record.price_cost = sum(fee_cost.price for fee_cost in fee_costs)
            else:
                record.price_cost = record.price_cost

    price_cost_wp = fields.Float(
        string="Cost / WP",
        digits=(16, 4),
        compute="_compute_price_cost_wp",
        store=True
    )

    @api.depends('revision_id.offer_kwp', 'price_cost')
    def _compute_price_cost_wp(self):
        for record in self:
            if record.revision_id.offer_kwp:
                record.price_cost_wp = record.price_cost / (record.revision_id.offer_kwp * 1000)
            elif record.type_direct_costs_id.name == 'Fee Cost':
                fee_costs = record.revision_id.revision_price_ids.filtered(
                    lambda r: r.type_price_id.name in ['Fee Externo', 'Fee Interno']
                )
                record.price_cost_wp = sum(fee_cost.price_wp for fee_cost in fee_costs)
            elif record.type_direct_costs_id.name == 'MBSV Solartree':
                fee_costs = record.revision_id.revision_price_ids.filtered(
                    lambda r: r.type_price_id.name in ['Gastos de estructura', 'Beneficio Industrial']
                )
                record.price_cost_wp = sum(fee_cost.price_wp for fee_cost in fee_costs)
            else:
                record.price_cost_wp = 0

    price_sale = fields.Monetary(
        string="Sale",
        currency_field="company_currency",
        compute="_compute_price_sale",
        digits=(16, 2),
        store=True
    )

    @api.depends('revision_id.revision_direct_costs_ids')
    def _compute_price_sale(self):
        for record in self:
            if record.type_direct_costs_id.name == 'BOP':
                direct_costs = record.revision_id.revision_direct_costs_ids.filtered(
                    lambda r: r.type_direct_costs_id.name in ['Modules', 'Inverter', 'Batery', 'Structure',
                                                              'Evacuation', 'H&S']
                )
                total_direct_costs = sum(direct_cost.price_sale for direct_cost in direct_costs)
                record.price_sale = record.revision_id.offer_price_rx - total_direct_costs
            else:
                record.price_sale = record.price_sale

    price_sale_wp = fields.Float(
        string="Sale / WP",
        digits=(16, 4),
        compute="_compute_price_wp",
        store=True
    )

    @api.depends('revision_id.offer_kwp', 'price_sale')
    def _compute_price_wp(self):
        for record in self:
            if record.revision_id.offer_kwp:
                record.price_sale_wp = record.price_sale / (record.revision_id.offer_kwp * 1000)
            else:
                record.price_sale_wp = 0


    company_currency = fields.Many2one(
        "res.currency",
        string='Currency',
        compute="_compute_company_currency",
        store=True
    )

    @api.depends('revision_id.lead_id.company_id')
    def _compute_company_currency(self):
        for record in self:
            if record.revision_id and record.revision_id.lead_id and record.revision_id.lead_id.company_id:
                record.company_currency = record.revision_id.lead_id.company_id.currency_id or self.env.company.currency_id
            else:
                record.company_currency = self.env.company.currency_id
