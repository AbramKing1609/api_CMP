from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import urllib3

# Desactiva solo el warning de certificados (Railway a veces da error SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="API CMP Perú", version="1.4")

def obtener_datos_cmp(cmp_number: str):
    base_url = "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/"
    data_url = "https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0 Safari/537.36",
        "Referer": base_url,
    }

    try:
        # Crear sesión para mantener cookies y encabezados
        session = requests.Session()
        session.get(base_url, headers=headers, timeout=10, verify=False)

        # Simular envío de formulario POST
        r = session.post(
            data_url,
            headers=headers,
            data={"cmp": cmp_number},
            timeout=10,
            verify=False
        )

        if r.status_code != 200:
            return {"error": f"Error HTTP {r.status_code} al acceder al servidor."}

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table tr")

        if len(rows) >= 2:
            celdas = rows[1].find_all("td")
            if len(celdas) >= 5:
                cmp = celdas[1].get_text(strip=True)
                ap_paterno = celdas[2].get_text(strip=True)
                ap_materno = celdas[3].get_text(strip=True)
                nombres = celdas[4].get_text(strip=True)

                return {
                    "CMP": cmp,
                    "Apellido_Paterno": ap_paterno,
                    "Apellido_Materno": ap_materno,
                    "Nombres": nombres,
                    "Nombre_Completo": f"{nombres} {ap_paterno} {ap_materno}"
                }

        return {"error": "No se encontraron resultados para ese CMP."}

    except requests.exceptions.SSLError:
        return {"error": "Error SSL: el servidor no pudo verificar el certificado."}
    except requests.exceptions.ConnectionError:
        return {"error": "Error de conexión con el sitio CMP."}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}

@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
