from datetime import date
from typing import List, Union

from pydantic import parse_obj_as

from sql_app import amo_query_schema, schemas
from sql_app import models


def handle_query(raw_list_of_leads: List[dict]) -> List[schemas.ResultLead]:
    def to_schema_many(data: List[dict]) -> List[amo_query_schema.Model]:
        return parse_obj_as(List[amo_query_schema.Model], data)

    def get_field_by_id(lead_values: amo_query_schema.Model, field_id: int) -> Union[str, None]:
        list_of_dicts = lead_values.custom_fields_values
        if list_of_dicts is None:
            return ''
        list_of_fields = list(filter(lambda f: f.field_id == field_id, list_of_dicts))
        if list_of_fields:
            field = list_of_fields[0]
            return field.values[0].value
        else:
            return ''

    def secs_to_date(secs: Union[int, str]) -> Union[date, None]:
        if not secs:
            return None
        else:
            secs = int(secs) + 15000
        return date.fromtimestamp(secs)

    list_of_leads = to_schema_many(raw_list_of_leads)

    gfbi = get_field_by_id
    fields = ['lead_id', 'material', 'specialist', 'deal_number', 'start_date', 'deal_duration', 'work_duration',
              'work_start']
    new_data = [models.Lead(**dict(zip(fields, [lead.id,
                                                gfbi(lead, 19713),
                                                gfbi(lead, 466963),
                                                gfbi(lead, 437987),
                                                secs_to_date(gfbi(lead, 942785)),
                                                gfbi(lead, 491089),
                                                gfbi(lead, 934909),
                                                secs_to_date(gfbi(lead, 942875))]))) for lead in
                list_of_leads]
    return new_data


def main():
    pass


if __name__ == '__main__':
    main()
