import zipfile
import io
import base64
import json
from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas import Grupo, Segmentacao
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict

router = APIRouter()

# Armazenamento temporário em memória
grupos: list[dict[str, list[Segmentacao]]] = []

@router.post("/groups")
def criar_grupo(payload: Grupo):
    grupo_id = str(uuid.uuid4())
    novo_grupo = {
        "id": grupo_id,
        "images": payload.images
    }
    grupos.append(novo_grupo)
    return {"message": "Grupo criado com sucesso", "group": novo_grupo}

@router.get("/groups")
def listar_grupos():
    return grupos

@router.delete("/groups/{group_id}")
def excluir_grupo(group_id: str):
    global grupos
    grupos_filtrados = [g for g in grupos if g["id"] != group_id] 
    if len(grupos_filtrados) == len(grupos):
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    grupos = grupos_filtrados
    return {"message": "Grupo excluído com sucesso"}

@router.get("/groups/{group_id}/download")
def download_grupo(group_id: str):
    # Buscar grupo pelo ID
    grupo = next((g for g in grupos if str(g["id"]) == str(group_id)), None)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Lista para gerar gráfico e areas.txt
        areas_info = []

        for img in grupo["images"]:
            # Adicionar imagem original
            #original_bytes = base64.b64decode(img.original.split(",")[1])
            #zipf.writestr(img.name, original_bytes)

            # Adicionar máscara
            mask_bytes = base64.b64decode(img.mask)
            nome_mask = img.name.rsplit('.', 1)[0] + "_segmentada.png"
            zipf.writestr(nome_mask, mask_bytes)

            areas_info.append({
                "imagem": img.name,
                "area": img.area,
                "data": img.data
            })

        # Criar areas.txt
        for area in areas_info:
            if isinstance(area["data"], date):
                area["data"] = area["data"].strftime("%d/%m/%Y")
            elif isinstance(area["data"], str) and "-" in area["data"]:
                try:
                    dt = datetime.strptime(area["data"], "%Y-%m-%d")
                    area["data"] = dt.strftime("%d/%m/%Y")
                except Exception:
                    pass

        # Criar JSON formatado
        areas_txt = json.dumps(areas_info, indent=2, ensure_ascii=False)
        zipf.writestr("areas.txt", areas_txt)

        df = pd.DataFrame(areas_info)
        df = df.sort_values(by=["data", "area"], ascending=[True, False])

        #caso haja datas repetidas
        contador = defaultdict(int)
        data_plot = []

        for data in df["data"]:
            if contador[data] == 0:
                data_plot.append(data)
            else:
                data_plot.append(f"{data} ({contador[data]})")
            contador[data] += 1

        df["data_plot"] = data_plot

        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10,5))
        #sns.lineplot(data=df, x="data", y="area", marker='o')
        sns.lineplot(data=df, x="data_plot", y="area", marker='o')
        plt.xlabel("Data")
        plt.xticks(rotation=45, ha='right')
        plt.ylabel("Área (px²)")
        plt.grid(True)

        img_buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img_buf, format="png")
        plt.close()
        img_buf.seek(0)

        zipf.writestr("grafico.png", img_buf.read())

    buffer.seek(0)
    filename = f"grupo_{group_id}.zip"
    return StreamingResponse(buffer, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })
