from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="API CMP Perú", version="1.1")

def obtener_datos_cmp(cmp_number: str):
    """
    Realiza la consulta al sitio del CMP directamente sin usar Selenium.
    """
    url = f"https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php?cmp={cmp_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/141.0.0.0 Safari/537.36",
        "Referer": "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/",
        "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()

        if "bloqueada" in r.text.lower():
            return {"error": "El sitio bloqueó la solicitud."}

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

    except requests.exceptions.RequestException as e:
        return {"error": f"Error de conexión: {str(e)}"}
    except Exception as e:
        return {"error": f"Error al procesar los datos: {str(e)}"}

@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
