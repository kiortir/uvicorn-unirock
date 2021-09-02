import time
from typing import Optional, List, Dict

from fastapi import FastAPI, Request, Depends
from querystring_parser import parser as qs_parser
from sqlalchemy.orm import Session

import settings
from amo_handlers.query_handler import handle_query
from amo_handlers.webhook_handler import handle_hook
from amo_oauth import *
from diagram_calc.diagram_calc import min_max_date
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

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
    def get_leads(a_token=access_token,
                  url="https://unirock.amocrm.ru/api/v4/leads?limit=250",
                  filter_query='%3Ffilter%5Btags_logic%5D=or&filter%3Ffilter%5Btags_logic%5D=or&filter%5Bpipe%5D%5B946942%5D%5B0%5D=18032857&filter%5Bpipe%5D%5B946942%5D%5B1%5D=18032860&filter%5Bpipe%5D%5B946942%5D%5B2%5D=18032863&filter%5Bpipe%5D%5B946942%5D%5B3%5D=18033010&filter%5Bpipe%5D%5B946942%5D%5B4%5D=18062053&filter%5Bpipe%5D%5B946942%5D%5B5%5D=39719170',
                  page=1) -> Optional[List[dict]]:
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
            return leads
        else:
            return leads + next_page

    data = get_leads()
    data = handle_query(data)

    crud.reset_leads(db, data)
    #
    # dayoffs = dates_calc.get_dayoffs()
    # a_data = list(map(partial(calc_data, dayoffs=dayoffs), data))
    # crud.reset_addition_values(db, a_data)


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


@app.get("/api/leads", response_model=Dict)
async def show_leads_machine(db: Session = Depends(get_db)):
    data = crud.show_leads(db)
    schema_data = [schemas.ResultLead.from_orm(x) for x in data]
    data = [(item[1] for item in lead) for lead in schema_data]

    dates = min_max_date([(lead.start_date, lead.deal_duration) for lead in schema_data])
    return {'min_max_date': dates,
            'leads': data}


@app.get("/leads", response_model=List[schemas.ResultLead])
async def show_leads(db: Session = Depends(get_db)):
    return crud.show_leads(db)


@app.post("/webhook/",
          description='Принимает webhook AmoCrm, обрабатывает его, и заносит в БД (если актуально)')
async def handle_webhook(q: Request, db: Session = Depends(get_db)):
    await check_token(db)
    query = await q.body()
    data = qs_parser.parse(query, normalized=True)
    z = await handle_hook(data=data, db=db)
    print(data)
    return {"status_code": z}


if __name__ == '__main__':
    pass
