from fastapi import FastAPI

from homework_api.database import classroom_conn
from homework_api.db_operations import create_table
from homework_api.routers import classroom, homework

app = FastAPI()

database = classroom_conn


@app.on_event("startup")
async def startup():
    await database.connect()

    # create tables if not exists
    await create_table(database)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(classroom.router)
app.include_router(homework.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
