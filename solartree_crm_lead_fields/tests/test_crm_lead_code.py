##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo.tests.common import TransactionCase


class TestSolartreeCrmLeadCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.crm_lead_model = cls.env["crm.lead"]

    def test_not_empty_lead_code(self):
        solartree_code = "OF/2024/0001"
        crm_lead = self.crm_lead_model.create(
            {
                "name": "Testing lead code",
                "solartree_code": solartree_code,
            }
        )
        self.assertNotEqual(crm_lead.code, "")
        self.assertEqual(crm_lead.code, solartree_code)

