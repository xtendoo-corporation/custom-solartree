from odoo import fields, models, api

class CrmLeadRevisionPrices(models.Model):
    _name = "crm.lead.revision.prices"
    _description = "Lead Revision Prices"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )
    type_price_id = fields.Many2one(
        "crm.lead.revision.price.type",
        string = "Revision Prices Type"
    )
    amount_euro = fields.Monetary(
        string="Amount",
        currency_field='company_currency',
    )
    amount_price_wp = fields.Monetary(
        string="Amount WP",
        currency_field='company_currency',
    )
    amount_percentage = fields.Float(
        string="Amount Percentage"
    )
    print_amount = fields.Float(
        string="Print Amount",
        compute="_compute_print_amount",
    )

    company_currency = fields.Many2one(
        "res.currency",
        string='Currency',
        compute="_compute_company_currency",
        store=True
    )

    @api.depends('amount_euro', 'amount_price_wp', 'amount_percentage')
    def _compute_print_amount(self):
        for record in self:
            if record.type_price_id.type == 'euro':
                record.print_amount = record.amount_euro
            elif record.type_price_id.type == 'percentage':
                record.print_amount = record.amount_percentage
            else:
                record.print_amount = 0

    @api.depends('revision_id.lead_id.company_id')
    def _compute_company_currency(self):
        for record in self:
            if record.revision_id and record.revision_id.lead_id and record.revision_id.lead_id.company_id:
                record.company_currency = record.revision_id.lead_id.company_id.currency_id or self.env.company.currency_id
            else:
                record.company_currency = self.env.company.currency_id
