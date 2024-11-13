from odoo import fields, models, api


class CrmLeadRevisionPrices(models.Model):
    _name = "crm.lead.revision.prices"
    _description = "Lead Revision Prices"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_price_id = fields.Many2one(
        "crm.lead.revision.global.type",
        string = "Type",
        domain = lambda self: self._domain_type_price_id(),
    )

    selected_type_price_ids = fields.Many2many(
        'crm.lead.revision.global.type',
        compute='_compute_selected_type_price_ids',
        store=False
    )

    @api.depends('revision_id.revision_price_ids.type_price_id')
    def _compute_selected_type_price_ids(self):
        for record in self:
            record.selected_type_price_ids = record.mapped('revision_id.revision_price_ids.type_price_id')

    def _domain_type_price_id(self):
        return [('id', 'not in', self.selected_type_price_ids.ids),
                ('behavior', '=', 'fee_and_margins')
                ]

    percentage = fields.Float(
        string="Percentage",
        compute="_compute_percentage",
        store=True
    )

    @api.depends('revision_id.revision_price_ids')
    def _compute_percentage(self):
        for record in self:
            if record.type_price_id.behavior_extra == "project":
                total_percentage = sum(
                    rec.percentage for rec in record.revision_id.revision_price_ids
                    if rec.type_price_id.project
                )
                record.percentage = total_percentage
            elif record.type_price_id.behavior_extra == "solartree":
                total_percentage = sum(
                    rec.percentage for rec in record.revision_id.revision_price_ids
                    if rec.type_price_id.solartree
                )
                record.percentage = total_percentage
            else:
                record.percentage = record.percentage

    price = fields.Monetary(
        string="Price",
        currency_field="company_currency",
        compute="_compute_price",
        store=True
    )

    @api.depends('revision_id.installation_sale_price', 'percentage')
    def _compute_price(self):
        for record in self:
            record.price = record.revision_id.installation_sale_price * record.percentage

    price_wp = fields.Monetary(
        string="Price / WP",
        currency_field="company_currency",
        digits=(16, 4),
        compute="_compute_price_wp",
        store=True
    )

    @api.depends('revision_id.offer_kwp', 'price')
    def _compute_price_wp(self):
        for record in self:
            if record.revision_id.offer_kwp:
                record.price_wp = record.price / (record.revision_id.offer_kwp * 1000)
            else:
                record.price_wp = 0

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
