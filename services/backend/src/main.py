from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from io import BytesIO
from PIL import Image, ImageDraw

from random import uniform

from routes.groups import router as groups_router
from routes.segmentations import router as segmentations_router

app = FastAPI()

app.include_router(groups_router)
app.include_router(segmentations_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/predict")
# async def predict(request: Request):
#     contents = await request.body()
#     image = Image.open(BytesIO(contents)).convert("RGB")

#     # Simula uma máscara
#     mask = Image.new("L", image.size, 255)
#     draw = ImageDraw.Draw(mask)
#     draw.rectangle([50, 50, 150, 150], fill=0)

#     # Simula cálculo da área da ferida
#     area = uniform(1, 9)

#     buffer = BytesIO()
#     mask.save(buffer, format="PNG")
#     mask_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

#     return JSONResponse(content={
#         "mask_base64": mask_base64,
#         "area": area
#     })
