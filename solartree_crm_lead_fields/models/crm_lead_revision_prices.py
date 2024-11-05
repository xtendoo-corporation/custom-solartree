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
    field_default = fields.Char(
        string="Field Default",
    )
    field_default_value = fields.Float(
        string="Field Default Value",
    )
    field_default_2 = fields.Char(
        string="Field Default 2",
    )
    field_default_value_2 = fields.Monetary(
        string="Field Default Value 2",
        currency_field='company_currency',
    )
    field_default_3 = fields.Char(
        string="Field Default 3",
    )
    field_default_value_3 = fields.Monetary(
        string="Field Default Value 3",
        currency_field='company_currency',
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
