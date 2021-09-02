from datetime import date
from typing import Union

from sqlalchemy.orm import Session

from sql_app import crud, models


async def handle_hook(data: dict, db: Session):
    IMPORTANT_STATUS = ['18032857', '18062053', '18032860', '18032863', '39719170', '18033010']
    l_ids = crud.get_ids(db)
    observed_leads = [str(x[0]) for x in l_ids]

    lead_info = data['leads']
    hook_type = list(lead_info.keys())[0]
    lead_fields = lead_info[hook_type][0]
    lead_id = lead_fields['id']
    status_id = lead_fields['status_id']

    def deserialize() -> models.Lead:
        def secs_to_date(secs: Union[int, str]) -> Union[date, None]:
            if secs == '':
                return None
            else:
                secs = int(secs) + 15000
            return date.fromtimestamp(secs)

        custom_fields = lead_fields.get('custom_fields', [])

        n_fields = models.Lead(
            lead_id=lead_id
        )
        for field in custom_fields:
            field['id'] = int(field['id'])
            if field['id'] == 19713:
                n_fields.material = field['values'][0]['value']
            if field['id'] == 466963:
                n_fields.specialist = field['values'][0]['value']
            if field['id'] == 437987:
                n_fields.deal_number = field['values'][0]['value']
            if field['id'] == 942785:
                time_value = int(field['values'][0])
                n_fields.start_date = secs_to_date(time_value)
            if field['id'] == 491089:
                n_fields.deal_duration = field['values'][0]['value']
            if field['id'] == 934909:
                n_fields.work_duration = field['values'][0]['value']
            if field['id'] == 942875:
                n_fields.work_start = secs_to_date(int(field['values'][0]))
        return n_fields

    if lead_id in observed_leads:
        if hook_type == 'delete' or status_id == '142':
            crud.delete_lead(db, lead_id)
        else:
            new_fields = deserialize()
            data = vars(new_fields)
            del data['_sa_instance_state']
            crud.update_lead(db, data)
    elif status_id in IMPORTANT_STATUS and hook_type != 'delete':
        data = deserialize()
        crud.insert_lead(db, data)
    return 200
