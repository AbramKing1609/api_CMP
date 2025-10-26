from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="API CMP Perú", version="2.0")

def obtener_datos_cmp(cmp_number: str):
    try:
        url = f"https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php?cmp={cmp_number}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15, verify=False)

        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, "html.parser")

        # Busca la tabla con clase cabecera_tr2
        row = soup.find("tr", {"class": "cabecera_tr2"})
        if not row:
            return {"error": "No se encontraron resultados para ese CMP."}

        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) < 5:
            return {"error": "No se encontraron suficientes datos."}

        datos = {
            "CMP": cells[1],
            "Apellido_Paterno": cells[2],
            "Apellido_Materno": cells[3],
            "Nombres": cells[4]
        }

        return datos

    except Exception as e:
        return {"error": str(e)}

@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
