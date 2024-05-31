from fastapi import APIRouter
from services.models import IrisFeatures
from core.model_ops import predict


prediction_router = APIRouter(
    tags=["prediction-service"],
)


@prediction_router.post(path='/predict')
async def prediction(features: IrisFeatures):
    response = predict(features)
    return {"prediction"}
