from odoo import fields, models, api


class CrmLeadRevisionTotalPriceRX(models.Model):
    _name = "crm.lead.revision.total.price.rx"
    _description = "Lead Revision Total Price RX"

    revision_id = fields.Many2one(
        "crm.lead.revision",
        required=True,
    )

    type_total_price_id = fields.Many2one(
        "crm.lead.revision.total.price.rx.type",
        string = "Type",
        domain = lambda self: self._domain_type_total_price_id(),
    )

    selected_type_total_price_ids = fields.Many2many(
        'crm.lead.revision.total.price.rx.type',
        compute='_compute_selected_type_total_price_ids',
        store=False
    )

    @api.depends('revision_id.revision_total_price_ids.type_total_price_id')
    def _compute_selected_type_total_price_ids(self):
        for record in self:
            record.selected_type_total_price_ids = record.mapped('revision_id.revision_total_price_ids.type_total_price_id')

    def _domain_type_total_price_id(self):
        return [('id', 'not in', self.selected_type_total_price_ids.ids)]

    price = fields.Float(
        string="Price",
        currency_field="company_currency",
    )

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

    # total_price_rx = fields.Float(
    #     string="Total Price RX",
    #     compute="_compute_total_price_rx",
    #     store=True
    # )
    #
    # @api.depends('revision_id.revision_total_price_ids.price')
    # def _compute_total_price_rx(self):
    #     for record in self:
    #         record.total_price_rx = sum(record.revision_id.revision_total_price_ids.mapped('price'))
    #         print("PRINT DESDE CRM LEAD REVISION TOTAL PRICE RX",record.total_price_rx)
