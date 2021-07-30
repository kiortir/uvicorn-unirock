from sql_app import amo_webhook_schema, crud, schemas, models
from datetime import datetime
from typing import Union
from sqlalchemy.orm import Session
from diagram_calc import diagram_calc


async def handle_hook(data: dict, db: Session):
    IMPORTANT_STATUS = ['18032857', '18062053', '18032860', '18032863', '39719170', '18033010']
    l_ids = crud.get_ids(db)
    observed_leads = [str(x[0]) for x in l_ids]

    lead_info = data['leads']
    hook_type = list(lead_info.keys())[0]
    lead_fields = lead_info[hook_type][0]
    lead_id = lead_fields['id']
    status_id = lead_fields['status_id']

    def serialize() -> models.Lead:
        def secs_to_date(secs: Union[int, str]) -> Union[datetime, None]:
            if secs == '':
                return None
            else:
                secs = int(secs)
            return datetime.fromtimestamp(secs)

        try:
            # none
            custom_fields = lead_fields['custom_fields']
        except KeyError:
            custom_fields = []
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
                new_fields.start_date = secs_to_date(time_value)
                # new_fields.start_date = to_date(time_value) + ' GMT+0300'
            if field['id'] == 491089:
                new_fields.deal_duration = field['values'][0]['value']
            if field['id'] == 934909:
                new_fields.work_duration = field['values'][0]['value']
            if field['id'] == 942875:
                new_fields.work_start = secs_to_date(int(field['values'][0]))
        return new_fields

    if lead_id in observed_leads:
        if hook_type == 'delete' or status_id == '142':
            crud.delete_lead(db, lead_id)
        else:
            new_fields = serialize()
            additional_data = diagram_calc.calc_data(new_fields)
            data = vars(new_fields)
            del data['_sa_instance_state']
            crud.update_lead(db, data)
            crud.update_additional_values(db, additional_data)
    else:
        if status_id in IMPORTANT_STATUS and hook_type != 'delete':
            data = serialize()
            additional_data = diagram_calc.calc_data(data)
            crud.insert_lead(db, data)
            crud
    return 200


# async def handle_hook(raw_list_of_leads: List[dict]) -> int:
#
# def handle_hook(data: dict, db=None,):  # -> schemas.ResultLead:
#
#     def to_schema(hook: dict) -> amo_webhook_schema.Model:
#         return amo_webhook_schema.Model.parse_obj(hook)
#
#     lead = to_schema(data)
#     if lead.leads.delete is not None:
#         crud.delete_lead(db, lead.leads.delete.field_0.id)
#         return True
#     else:
#         lead_fields = lead.leads.update.field_0
#     lead_status = lead.leads.update.field_0.status_id
#     if lead_status == '142':
#         crud.delete_lead(db, lead.leads.update.field_0.id)
#     new_fields = schemas.ResultLead
#     new_fields.lead_id = lead_fields.id
#
#     def secs_to_date(secs: Union[int, str]) -> Union[datetime, None]:
#         if secs == '':
#             return None
#         else:
#             secs = int(secs)
#         return datetime.fromtimestamp(secs)
#
#     custom_fields = lead_fields.custom_fields
#     if custom_fields is not None:
#         for field in custom_fields.values():
#             print(field)
#             field['id'] = int(field['id'])
#             if field['id'] == 19713:
#                 new_fields.material = field['values'][0]['value']
#             if field['id'] == 466963:
#                 new_fields.specialist = field['values'][0]['value']
#             if field['id'] == 437987:
#                 new_fields.deal_number = field['values'][0]['value']
#             if field['id'] == 942785:
#                 time_value = int(field['values'][0])
#                 new_fields.start_date = secs_to_date(time_value)
#             if field['id'] == 491089:
#                 new_fields.deal_duration = field['values'][0]['value']
#             if field['id'] == 934909:
#                 new_fields.work_duration = field['values'][0]['value']
#             if field['id'] == 942875:
#                 new_fields.work_start = secs_to_date(int(field['values'][0]))
#
#
#     return new_fields.material
