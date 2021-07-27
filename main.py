import time
from typing import Optional, List

from fastapi import FastAPI, Request, Depends
from querystring_parser import parser as qsparser
from sqlalchemy.orm import Session

import settings
from amo_oauth import *
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine
from webhook_handler import handle_hook

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def update_token(db: Session = Depends(get_db), token_type: str = 'refresh_token'):
    token = crud.get_token(db, token_type=token_type)
    new_tokens = get_new_tokens(token, token_type)
    crud.update_lead(db, new_tokens)


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
    def collapse_json(leads):
        specialist_list = []
        for index, lead in enumerate(leads):
            lead_id = lead['id']
            # material = specialist = deal_number = start_date = deal_duration = work_duration = work_start = date_in_secs = ''
            lead_data = models.Lead(
                lead_id=lead_id
            )
            custom_fields_values = lead['custom_fields_values']
            for field in custom_fields_values:
                if field['field_id'] == 19713:
                    lead_data.material = field['values'][0]['value']
                if field['field_id'] == 466963:
                    lead_data.specialist = field['values'][0]['value']
                if field['field_id'] == 437987:
                    lead_data.deal_number = field['values'][0]['value']
                if field['field_id'] == 942785:
                    lead_data.secs = field['values'][0]['value']
                    lead_data.start_date = time.ctime(field['values'][0]['value'] + 10800) + ' GMT+0300'
                if field['field_id'] == 491089:
                    lead_data.deal_duration = field['values'][0]['value']
                if field['field_id'] == 934909:
                    lead_data.work_duration = field['values'][0]['value']
                if field['field_id'] == 942875:
                    lead_data.work_start = time.ctime(field['values'][0]['value'] + 10800) + ' GMT+0300'
            specialist_list.append(lead_data)
        return specialist_list

    def get_leads(a_token=access_token,
                  url="https://unirock.amocrm.ru/api/v4/leads?limit=250",
                  filter_query='%3Ffilter%5Btags_logic%5D=or&filter%3Ffilter%5Btags_logic%5D=or&filter%5Bpipe%5D%5B946942%5D%5B0%5D=18032857&filter%5Bpipe%5D%5B946942%5D%5B1%5D=18032860&filter%5Bpipe%5D%5B946942%5D%5B2%5D=18032863&filter%5Bpipe%5D%5B946942%5D%5B3%5D=18033010&filter%5Bpipe%5D%5B946942%5D%5B4%5D=18062053&filter%5Bpipe%5D%5B946942%5D%5B5%5D=39719170',
                  page=1):
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
            f_leads = collapse_json(leads)
            return f_leads
        else:

            return leads + next_page

    crud.reset_leads(db, get_leads())


@app.get("/test/{lead_id}", response_model=schemas.Lead)
async def test(lead_id: int, db: Session = Depends(get_db)):
    z = crud.get_lead(db, lead_id)
    return z


@app.get("/")
async def root():
    return {"app": "running"}


@app.get('/auth',
         description="Обновляет токены по auth токену. Можно передать в запросе или через окружение")
async def auth(q: Optional[str] = None):
    if q:
        auth_token = q
    else:
        auth_token = settings.auth_token()
    update_token(token_type=auth_token)
    return {'result': 'success!'}


@app.get("/refresh")
async def refresh(db: Session = Depends(get_db)):
    access_token = crud.get_token(db, 'access_token')
    refresh_leads(access_token, db=db)
    return {"refresh: 'success'"}


@app.get("/leads", response_model=List[schemas.Lead])
async def show_leads(db: Session = Depends(get_db)):
    return crud.show_leads(db)


@app.post("/webhook/",
          description='Принимает webhook AmoCrm, обрабатывает его, и заносит в БД (если актуально)')
async def handle_webhook(q: Request, db: Session = Depends(get_db)):
    await check_token(db)
    query = await q.body()
    data = qsparser.parse(query, normalized=True)
    z = await handle_hook(data=data, db=db)
    return {"status_code": z}


if __name__ == '__main__':
    pass
