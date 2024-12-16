from odoo import fields, models, api


class CrmLeadRevisionDirectCosts(models.Model):
    _name = "crm.lead.revision.direct.costs"
    _description = "Lead Revision Direct Costs"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    lead_id = fields.Many2one(
        related="revision_id.lead_id",
        string="Opportunity",
        store=True,
        readonly=True
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
        store=True
    )

    price_cost_wp = fields.Float(
        string="€/WP",
        digits=(16, 4),
        compute="_compute_price_cost_wp",
        store=True
    )

    @api.depends('revision_id.offer_kwp', 'price_cost')
    def _compute_price_cost_wp(self):
        for record in self:
            if record.revision_id.offer_kwp:
                record.price_cost_wp = record.price_cost / (record.revision_id.offer_kwp * 1000)
            else:
                record.price_cost_wp = 0

    price_sale = fields.Monetary(
        string="Sale",
        currency_field="company_currency",
        store=True
    )

    price_sale_wp = fields.Float(
        string="€/WP",
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
