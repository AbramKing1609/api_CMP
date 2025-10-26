from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import os

app = FastAPI(title="API CMP Perú", version="1.0")

def obtener_datos_cmp(cmp_number: str):
    url = f"https://aplicaciones.cmp.org.pe/conoce_a_tu_medico/datos-colegiado.php?cmp={cmp_number}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # 👉 Usa el Chrome y driver del contenedor, no webdriver_manager
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 15)
    datos = {}

    try:
        driver.get(url)
        print("🌐 Cargando:", driver.title)

        table = wait.until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(., 'Detalle')]"))
        )
        rows = table.find_elements(By.TAG_NAME, "tr")

        if len(rows) >= 2:
            celdas = rows[1].find_elements(By.TAG_NAME, "td")
            if len(celdas) >= 5:
                datos = {
                    "CMP": celdas[1].text.strip(),
                    "Apellido_Paterno": celdas[2].text.strip(),
                    "Apellido_Materno": celdas[3].text.strip(),
                    "Nombres": celdas[4].text.strip()
                }
            else:
                datos = {"error": "Datos incompletos en la fila."}
        else:
            datos = {"error": "No se encontraron resultados para ese CMP."}

    except Exception as e:
        datos = {"error": str(e)}
    finally:
        driver.quit()

    return datos


@app.get("/consulta")
def consulta_cmp(cmp: str = Query(..., description="Número CMP del médico")):
    datos = obtener_datos_cmp(cmp)
    return JSONResponse(content=datos)
