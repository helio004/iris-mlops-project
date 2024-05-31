import uvicorn

from fastapi import FastAPI

from services.health_service import health_router
from services.predict_service import prediction_router


app = FastAPI()

app.include_router(router=prediction_router)
app.include_router(router=health_router)


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000,
        access_log=True,
        log_config=None,
        workers=1,
    )