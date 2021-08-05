import time
from typing import Optional, List, Union
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from querystring_parser import parser as qs_parser
from sqlalchemy.orm import Session
from functools import partial
import settings
from amo_oauth import *
from sql_app import crud, models, schemas, amo_query_schema
from sql_app.database import SessionLocal, engine
from amo_handlers.query_handler import handle_query
from amo_handlers.webhook_handler import handle_hook
from diagram_calc.diagram_calc import calc_data, dates_calc

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def update_token(db: Session, token_type: str = 'refresh_token', token: str = None):
    if token is None:
        token = crud.get_token(db, token_type=token_type)
    # token = crud.get_token(db, token_type=token_type)
    new_tokens = get_new_tokens(token, token_type)
    crud.set_tokens(db, new_tokens)


async def check_token(db: Session = Depends(get_db)):
    def token_expired():
        exp_time = crud.get_token(db, 'expiration_time')
        now = time.time()
        return now > float(exp_time)

    if token_expired():
        await update_token(db)
        return True
    return False


def refresh_leads(access_token: str, db: Session = Depends(get_db)):
    # def collapse_json(leads):
    #     specialist_list = []
    #     for index, lead in enumerate(leads):
    #         lead_id = lead['id']
    #         # material = specialist = deal_number = start_date = deal_duration = work_duration = work_start = date_in_secs = ''
    #         lead_data = models.Lead(
    #             lead_id=lead_id
    #         )
    #         custom_fields_values = lead['custom_fields_values']
    #         for field in custom_fields_values:
    #             if field['field_id'] == 19713:
    #                 lead_data.material = field['values'][0]['value']
    #             if field['field_id'] == 466963:
    #                 lead_data.specialist = field['values'][0]['value']
    #             if field['field_id'] == 437987:
    #                 lead_data.deal_number = field['values'][0]['value']
    #             if field['field_id'] == 942785:
    #                 lead_data.secs = field['values'][0]['value']
    #                 lead_data.start_date = datetime.fromtimestamp(int(field['values'][0]['value'])).strftime("%b %d %Y")
    #                 # lead_data.start_date = time.ctime(field['values'][0]['value'] + 10800) + ' GMT+0300'
    #             if field['field_id'] == 491089:
    #                 lead_data.deal_duration = field['values'][0]['value']
    #             if field['field_id'] == 934909:
    #                 lead_data.work_duration = field['values'][0]['value']
    #             if field['field_id'] == 942875:
    #                 lead_data.work_start = time.ctime(field['values'][0]['value'] + 10800) + ' GMT+0300'
    #         specialist_list.append(lead_data)
    #     return specialist_list

    def get_leads(a_token=access_token,
                  url="https://unirock.amocrm.ru/api/v4/leads?limit=250",
                  filter_query='%3Ffilter%5Btags_logic%5D=or&filter%3Ffilter%5Btags_logic%5D=or&filter%5Bpipe%5D%5B946942%5D%5B0%5D=18032857&filter%5Bpipe%5D%5B946942%5D%5B1%5D=18032860&filter%5Bpipe%5D%5B946942%5D%5B2%5D=18032863&filter%5Bpipe%5D%5B946942%5D%5B3%5D=18033010&filter%5Bpipe%5D%5B946942%5D%5B4%5D=18062053&filter%5Bpipe%5D%5B946942%5D%5B5%5D=39719170',
                  page=1) -> Union[List[schemas.ResultLead], None]:
        url = f"{url}&{filter_query}&page={page}"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer %s" % a_token
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200 and response.status_code != 204:
            raise Exception(f"Status code: {response.status_code}; response: {response.content}")
        if response.status_code == 204:  # выход из рекурсии
            return None
        leads = response.json()['_embedded']['leads']
        next_page = get_leads(page=page + 1)
        if next_page is None:
            # f_leads = collapse_json(leads)
            f_leads = handle_query(leads)
            return f_leads
        else:
            return leads + next_page

    data = get_leads()
    crud.reset_leads(db, data)

    dayoffs = dates_calc.get_dayoffs()
    a_data = list(map(partial(calc_data, dayoffs=dayoffs), data))
    crud.reset_addition_values(db, a_data)


@app.get("/test/{lead_id}", response_model=schemas.ResultLead)
async def test(lead_id: int, db: Session = Depends(get_db)):
    z = crud.get_lead(db, lead_id)
    return z


@app.get("/")
async def root():
    return {"app": "running"}


@app.get('/auth/{q}',
         description="Обновляет токены по auth токену. Можно передать в запросе или через окружение")
async def auth(db: Session = Depends(get_db), q: Optional[str] = None):
    if q:
        auth_token = q
    else:
        auth_token = settings.auth_token()

    await update_token(db=db, token_type=auth_token, token=q)
    return {'result': 'success!'}


@app.get('/reload-tokens',
         description="Обновляет токены по refresh токену",
         status_code=200)
async def reload_tokens(db: Session = Depends(get_db)):
    await update_token(db, token_type='refresh_token')
    return {"reload: 'success'"}


@app.get("/refresh",
         description='сбрасывает и обновляет БД')
async def refresh(db: Session = Depends(get_db)):
    access_token = crud.get_token(db, 'access_token')
    refresh_leads(access_token, db=db)
    return {"refresh: 'success'"}


@app.get("/api/leads")#, response_model=List[List])
async def show_leads_machine(db: Session = Depends(get_db)):
    data = crud.show_leads(db)
    print(data[1].work_duration)
    schema_data = [schemas.ResultLead.from_orm(x) for x in data]
    data = [(x[1] for x in y) for y in schema_data]
    return data


@app.get("/leads", response_model=List[schemas.ResultLead])
async def show_leads(db: Session = Depends(get_db)):
    return crud.show_leads(db)


@app.get("/a-leads")  # , response_model=List[schemas.AdditionalLead])
async def show_add_leads(db: Session = Depends(get_db)):
    return crud.show_add_leads(db)


@app.post("/webhook/",
          description='Принимает webhook AmoCrm, обрабатывает его, и заносит в БД (если актуально)')
async def handle_webhook(q: Request, db: Session = Depends(get_db)):
    await check_token(db)
    query = await q.body()
    data = qs_parser.parse(query, normalized=True)
    z = await handle_hook(data=data, db=db)
    return {"status_code": z}


@app.get('/access')
async def tok(db: Session = Depends(get_db)):
    return crud.get_token(db, 'access_token')


if __name__ == '__main__':
    import json

    string = "leads%5Bupdate%5D%5B0%5D%5Bid%5D=23435433&leads%5Bupdate%5D%5B0%5D%5Bname%5D=%D0%9D%D0%B8%D0%BA%D0%B8%D1%82%D0%B0+79169849777&leads%5Bupdate%5D%5B0%5D%5Bstatus_id%5D=17965459&leads%5Bupdate%5D%5B0%5D%5Bold_status_id%5D=21632815&leads%5Bupdate%5D%5B0%5D%5Bprice%5D=0&leads%5Bupdate%5D%5B0%5D%5Bresponsible_user_id%5D=6499114&leads%5Bupdate%5D%5B0%5D%5Blast_modified%5D=1627306719&leads%5Bupdate%5D%5B0%5D%5Bmodified_user_id%5D=6499114&leads%5Bupdate%5D%5B0%5D%5Bcreated_user_id%5D=0&leads%5Bupdate%5D%5B0%5D%5Bdate_create%5D=1621622403&leads%5Bupdate%5D%5B0%5D%5Bpipeline_id%5D=936736&leads%5Bupdate%5D%5B0%5D%5Btags%5D%5B0%5D%5Bid%5D=440737&leads%5Bupdate%5D%5B0%5D%5Btags%5D%5B0%5D%5Bname%5D=form&leads%5Bupdate%5D%5B0%5D%5Baccount_id%5D=16700680&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B0%5D%5Bid%5D=436799&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B0%5D%5Bname%5D=utm_medium&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B0%5D%5Bcode%5D=UTM_MEDIUM&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B1%5D%5Bid%5D=439295&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B1%5D%5Bname%5D=utm_campaign&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B1%5D%5Bcode%5D=UTM_CAMPAIGN&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bid%5D=467289&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bname%5D=%D0%9C%D0%B5%D0%BD%D0%B5%D0%B4%D0%B6%D0%B5%D1%80+%D0%BF%D0%BE+%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B6%D0%B0%D0%BC&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=%D0%92%D0%BB%D0%B0%D0%B4%D0%B0+%D0%A0%D1%8B%D1%82%D0%BE%D0%B2%D0%B0&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B2%5D%5Bvalues%5D%5B0%5D%5Benum%5D=960551&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bid%5D=473357&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bname%5D=%D0%9F%D1%80%D0%B8%D0%BC%D0%B5%D1%87%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BA+%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7%D1%83&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B3%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=%D0%B6%D0%B8%D0%B2%D0%B5%D1%82+%D0%BD%D0%B0+%D1%80%D1%8F%D0%B7%D0%B0%D0%BD%D1%81%D0%BA%D0%BE%D0%BC+%D0%BF%D1%80%D0%BE%D1%81%D0%BF%D0%B5%D0%BA%D1%82%D0%B5%2C+%D0%BD%D0%B0+%D1%81%D1%82%D0%BE%D0%BB%D0%B5%D1%88%D0%BD%D0%B8%D1%86%D0%B5+%D1%81%D1%82%D0%B0%D0%BB+%D0%BE%D0%B1%D0%BB%D0%B5%D0%B7%D0%B0%D1%82%D1%8C+%D0%BA%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C%2C+%D1%85%D0%BE%D1%82%D1%8F%D1%82+%D0%BD%D0%BE%D0%B2%D1%83%D1%8E.%0A%D0%BF%D0%BE+%D1%81%D1%82%D0%BE%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C+%D0%B4%D0%B5%D0%BC%D0%BE%D0%BD%D1%82%D0%B0%D0%B6%D0%B0+%D1%83%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BB%D0%B0+%D1%83+%D0%A0%D0%BE%D0%BC%D1%8B%2C+%D0%BE%D0%B7%D0%B2%D1%83%D1%87%D0%B8%D0%BB%D0%B0+6%D0%BA%0A%D0%BF%D1%80%D0%B8%D0%B5%D0%B4%D0%B5%D1%82+%D1%81%D0%BC%D0%BE%D1%82%D1%80%D0%B5%D1%82%D1%8C+%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D1%86%D1%8B%0A%0A%D0%9F-%D0%BE%D0%B1%D1%80+%D1%81%D1%82%D0%BE%D0%BB%D0%B5%D1%88%D0%BD%D0%B8%D1%86%D0%B0%0A1800%2A2400%2A2200%D0%BC%D0%BC+630%D0%BC%D0%BC%0A%D0%9A%D1%80%D0%BE%D0%BC%D0%BA%D0%B0%3A+40%D0%BC%D0%BC%0A%D0%91%D0%BE%D1%80%D1%82%D0%B8%D0%BA%3A+40%D0%BC%D0%BC%0A%D0%92%D1%8B%D1%80%D0%B5%D0%B7%D1%8B%3A+%D0%92%D0%9F%2C+%D0%BC%D0%BE%D0%B9%D0%BA%D0%B0+%D0%BD%D0%B8%D0%B6%D0%BD%D0%B5%D0%B3%D0%BE+%D0%BA%D1%80%D0%B5%D0%BF%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F%2C%D1%81%D0%BC%D0%B5%D1%81%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%0A%0A%D0%A4%D0%B0%D1%80%D1%82%D1%83%D0%BA%0A2400%2A1400%2A600%D0%BC%D0%BC%0A%D0%92%D1%8B%D1%80%D0%B5%D0%B7%D1%8B%3A+%D1%82%D1%80%D0%B8+%D1%80%D0%BE%D0%B7%D0%B5%D1%82%D0%BA%D0%B8%2C+%D1%81%D1%87%D0%B5%D1%82%D1%87%D0%B8%D0%BA+%0A%0ACaesarstone+Dreamy+Marfil+5220++%3D+++188%C2%A0127%2C70+%E2%82%BD+%09%0ATechnistone+NOBLE+BOTTICINO%3D++++148%C2%A0531%2C30+%E2%82%BD+%09%0AVicostone+Taj+Mahal+BQ+9453%3D+++159%C2%A0210%2C70+%E2%82%BD+%09%0Ahttps%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2F1IOMjx2knhPjgjzlql4Rf4tYzSi13s5HMxRPRk3Z7yY8%2Fedit%3Fusp%3Dsharing&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bid%5D=435829&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bname%5D=r7k12id&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B4%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=6891910591&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B5%5D%5Bid%5D=475185&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B5%5D%5Bname%5D=%D0%98%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA+%D1%82%D1%80%D0%B0%D1%84%D0%B8%D0%BA%D0%B0&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B5%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=yandex&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B6%5D%5Bid%5D=436839&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B6%5D%5Bname%5D=%D0%9A%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D0%BE%D0%B5+%D1%81%D0%BB%D0%BE%D0%B2%D0%BE&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B6%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=caesarstone+5220&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B7%5D%5Bid%5D=482151&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B7%5D%5Bname%5D=%D0%A2%D0%B8%D0%BF+%D1%83%D1%81%D1%82%D1%80%D0%BE%D0%B9%D1%81%D1%82%D0%B2%D0%B0&leads%5Bupdate%5D%5B0%5D%5Bcustom_fields%5D%5B7%5D%5Bvalues%5D%5B0%5D%5Bvalue%5D=mobile&leads%5Bupdate%5D%5B0%5D%5Bcreated_at%5D=1621622403&leads%5Bupdate%5D%5B0%5D%5Bupdated_at%5D=1627306719&account%5Bsubdomain%5D=unirock&account%5Bid%5D=16700680&account%5B_links%5D%5Bself%5D=https%3A%2F%2Funirock.amocrm.ru"
