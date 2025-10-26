from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="API CMP Perú", version="2.0")

# Tu clave de ScraperAPI
SCRAPERAPI_KEY = "197b15468b8ecdf85ff915d344c53d48"
BASE_URL = "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php"

def obtener_datos_cmp(cmp_number: str):
    """
    Obtiene los datos del médico desde CMP usando ScraperAPI.
    """
    try:
        # Construimos la URL del proxy ScraperAPI
        proxy_url = f"http://api.scraperapi.com"
        params = {
            "api_key": SCRAPERAPI_KEY,
            "url": f"{BASE_URL}?cmp={cmp_number}",
            "render": "true",  # permite cargar JS y contenido dinámico
            "country_code": "PE"
        }

        # Petición
        r = requests.get(proxy_url, params=params, timeout=30)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table tr")

        # Revisar estructura HTML
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
                    "status": "Encontrado"
                }

        # Si no hay resultados visibles
        return {"error": "No se encontraron resultados para ese CMP o la estructura cambió."}

    except Exception as e:
        return {"error": f"Error de conexión: {str(e)}"}


@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    """
    Endpoint principal para consultar datos de médicos por CMP.
    """
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
