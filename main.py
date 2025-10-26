from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="API CMP Perú", version="1.5")

SCRAPINGBEE_KEY = "JZ1LZ47IK8QDHR09YOOWURL26ZL8ORVQ5SU4ISKG8H6G4EGVA82JSR0XB02KVVD5VIL3VO5P26XQLNXF"  # 🔑 crea cuenta gratuita en scrapingbee.com

def obtener_datos_cmp(cmp_number: str):
    data_url = "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php"

    try:
        payload = {"cmp": cmp_number}
        params = {
            "api_key": SCRAPINGBEE_KEY,
            "url": data_url,
            "render_js": "false"
        }

        r = requests.post("https://app.scrapingbee.com/api/v1/", params=params, data=payload, timeout=20)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table tr")

        if len(rows) >= 2:
            celdas = rows[1].find_all("td")
            if len(celdas) >= 5:
                return {
                    "CMP": celdas[1].get_text(strip=True),
                    "Apellido_Paterno": celdas[2].get_text(strip=True),
                    "Apellido_Materno": celdas[3].get_text(strip=True),
                    "Nombres": celdas[4].get_text(strip=True),
                    "Nombre_Completo": f"{celdas[4].get_text(strip=True)} "
                                       f"{celdas[2].get_text(strip=True)} "
                                       f"{celdas[3].get_text(strip=True)}",
                    "status": "Encontrado ✅"
                }

        return {"error": "No se encontraron resultados para ese CMP."}

    except Exception as e:
        return {"error": f"Error: {str(e)}"}


@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
