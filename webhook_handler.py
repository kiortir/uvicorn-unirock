from time import ctime as to_date

from sqlalchemy.orm import Session

from sql_app import crud, models


async def handle_hook(data: dict, db: Session) -> int:
    IMPORTANT_STATUS = ['18032857', '18062053', '18032860', '18032863', '39719170', '18033010']
    l_ids = crud.get_ids(db)
    observed_leads = [str(x[0]) for x in l_ids]

    lead_info = data['leads']
    hook_type = list(lead_info.keys())[0]
    lead_fields = lead_info[hook_type][0]
    lead_id = lead_fields['id']
    status_id = lead_fields['status_id']

    def serialize() -> models.Lead:
        custom_fields = lead_fields['custom_fields']
        new_fields = models.Lead(
            lead_id=lead_id
        )
        for field in custom_fields:
            field['id'] = int(field['id'])
            if field['id'] == 19713:
                new_fields.material = field['values'][0]['value']
            if field['id'] == 466963:
                new_fields.specialist = field['values'][0]['value']
            if field['id'] == 437987:
                new_fields.deal_number = field['values'][0]['value']
            if field['id'] == 942785:
                time_value = int(field['values'][0])
                new_fields.secs = time_value
                new_fields.start_date = to_date(time_value) + ' GMT+0300'
            if field['id'] == 491089:
                new_fields.deal_duration = field['values'][0]['value']
            if field['id'] == 934909:
                new_fields.work_duration = field['values'][0]['value']
            if field['id'] == 942875:
                new_fields.work_start = to_date(int(field['values'][0]))
        return new_fields

    if lead_id in observed_leads:
        if hook_type == 'delete' or status_id == '142':
            crud.delete_lead(db, lead_id)
        else:
            data = vars(serialize())
            del data['_sa_instance_state']
            crud.update_lead(db, data)
    else:
        if status_id in IMPORTANT_STATUS and hook_type != 'delete':
            data = serialize()
            crud.insert_lead(db, data)
    return 200
