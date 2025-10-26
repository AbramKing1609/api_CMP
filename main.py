from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="API CMP Perú", version="1.3")

def obtener_datos_cmp(cmp_number: str):
    base_url = "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/"
    data_url = "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0 Safari/537.36",
        "Referer": base_url,
    }

    try:
        # Crear sesión para mantener cookies
        session = requests.Session()
        session.get(base_url, headers=headers, timeout=10, verify=False)

        # Simular el formulario (método POST)
        r = session.post(data_url, headers=headers, data={"cmp": cmp_number}, timeout=10, verify=False)
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
                                       f"{celdas[3].get_text(strip=True)}"
                }

        return {"error": "No se encontraron resultados para ese CMP."}

    except Exception as e:
        return {"error": f"Error: {str(e)}"}

@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
