from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from schemas import Segmentacao

import torch
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import os

import modelo 

router = APIRouter()

# Armazenamento temporário em memória
segmentacoes = []

# Carregar modelo
def load_model(filename, learning_rate, device='cpu'):
    model = modelo.UNet(in_channels=3, out_channels=1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    checkpoint = torch.load(filename, map_location=torch.device(device))
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    
    model.eval()
    return model

modelo_carregado = load_model(os.path.join(os.path.dirname(__file__), '..', 'Unet_run1.pt'), learning_rate=0.001)

# Função para gerar segmentação
def processar_imagem(image: Image.Image):
    img_array = np.array(image.convert("RGB").resize((256,256)))
    img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0)

    with torch.no_grad():
        output = modelo_carregado(img_tensor)
        mask = torch.sigmoid(output).squeeze().numpy()
        mask = (mask > 0.5).astype(np.uint8)

    area_segmentada = np.sum(mask > 0)

    # Converte a máscara para imagem do tipo PIL para retorno
    mask_img = Image.fromarray((mask * 255).astype(np.uint8)).resize(image.size)

    buffer = BytesIO()
    mask_img.save(buffer, format="PNG")
    mask_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return mask_base64, int(area_segmentada)

# =============================================
# Endpoints
@router.post("/predict")
async def predict(request: Request):
    contents = await request.body()
    image = Image.open(BytesIO(contents)).convert("RGB")

    mask_base64, area = processar_imagem(image)

    return JSONResponse(content={
        "mask_base64": mask_base64,
        "area": area
    })

@router.post("/segmentations")
def criar_segmentacao(data: Segmentacao):
    segmentacoes.append(data)
    return {"message": "Segmentação salva com sucesso"}

@router.get("/segmentations")
def listar_segmentacoes():
    return segmentacoes

@router.delete("/segmentations/{name}")
def excluir_segmentacao(name: str):
    global segmentacoes
    antes = len(segmentacoes)
    segmentacoes = [s for s in segmentacoes if s.name != name]
    if len(segmentacoes) == antes:
        raise HTTPException(status_code=404, detail="Segmentação não encontrada")
    return {"message": f"Segmentação '{name}' excluída com sucesso"}

# =============================================