from . import models

def create_code_equal_to_id(env):
    env.cr.execute("ALTER TABLE crm_lead ADD COLUMN solartree_code character varying;")
    env.cr.execute("UPDATE crm_lead SET solartree_code = id;")


def assign_old_sequences(env):
    lead_obj = env["crm.lead"]
    sequence_obj = env["ir.sequence"]
    leads = lead_obj.search([], order="id")
    for lead_id in leads.ids:
        env.cr.execute(
            "UPDATE crm_lead SET solartree_code = %s WHERE id = %s;",
            (
                sequence_obj.next_by_code("crm.lead"),
                lead_id,
            ),
        )
