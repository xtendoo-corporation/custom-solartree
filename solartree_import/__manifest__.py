{
    "name": "SolarTree Import",
    "summary": """SolarTree Import""",
    "version": "17.0.1.0.0",
    "author":
        "Salvador Gonzalez (Xtendoo)",
    "category": "CRM",
    "license": "AGPL-3",
    "depends": [
        "solartree_crm_lead_fields",
        "crm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "wizards/crm_lead_import_wizard_view.xml",
        "wizards/crm_lead_import_partial_wizard_view.xml",
    ],
    "installable": True,
}
