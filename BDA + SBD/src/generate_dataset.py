"""
Generador de dataset de solicitudes de vivienda juvenil en Euskadi.
Usa únicamente librerías estándar (csv, random, math) para máxima velocidad y fiabilidad.
"""
import csv
import random
import math
from pathlib import Path

def generar_datos_csv(n_samples: int = 1200, seed: int = 42):
    random.seed(seed)
    municipios = [
        ("Bilbao", 0.35, 850),
        ("Donostia-San Sebastián", 0.20, 1100),
        ("Vitoria-Gasteiz", 0.25, 670),
        ("Barakaldo", 0.12, 720),
        ("Getxo", 0.08, 980)
    ]
    mun_names = [m[0] for m in municipios]
    mun_weights = [m[1] for m in municipios]
    mun_precios = {m[0]: m[2] for m in municipios}

    contratos = ["Indefinido", "Temporal", "En_Practicas", "Autonomo"]
    contrato_weights = [0.45, 0.30, 0.15, 0.10]

    subvenciones = ["Gaztelagun", "Emantzipa", "VPO_Alquiler"]
    subv_weights = [0.55, 0.25, 0.20]

    filas = []
    headers = [
        "solicitud_id", "municipio", "edad", "tipo_contrato",
        "ingresos_mensuales", "precio_alquiler", "antiguedad_laboral_meses",
        "ahorros_disponibles", "comparte_piso", "deudas_mensuales",
        "tipo_subvencion", "es_viable"
    ]

    for i in range(1, n_samples + 1):
        sol_id = f"SOL-2026-{1000 + i}"
        mun = random.choices(mun_names, weights=mun_weights, k=1)[0]
        
        # Edad con 12% nulos
        if random.random() < 0.12:
            edad_str = ""
            edad_num = 26
        else:
            edad_num = random.randint(18, 34)
            edad_str = str(edad_num)

        contrato = random.choices(contratos, weights=contrato_weights, k=1)[0]
        ingresos = max(750.0, min(3200.0, random.gauss(1380.0, 300.0)))
        
        precio_base = mun_precios[mun]
        alquiler = max(400.0, min(1600.0, random.gauss(precio_base, 100.0)))

        antiguedad = max(1.0, min(96.0, random.expovariate(1.0 / 18.0)))
        
        # Ahorros con 8% nulos
        if random.random() < 0.08:
            ahorros_str = ""
            ahorros_num = 1500.0
        else:
            ahorros_num = max(0.0, min(25000.0, random.expovariate(1.0 / 3500.0)))
            ahorros_str = str(round(ahorros_num, 2))

        comparte = "Si" if random.random() < 0.35 else "No"
        deudas = random.choices([0.0, 80.0, 160.0, 280.0], weights=[0.60, 0.20, 0.14, 0.06], k=1)[0]
        subv = random.choices(subvenciones, weights=subv_weights, k=1)[0]

        # Cálculo de viabilidad real
        alquiler_efectivo = alquiler / 2.0 if comparte == "Si" else alquiler
        subv_monto = 300.0 if subv == "Gaztelagun" else (250.0 if subv == "Emantzipa" else 350.0)
        alquiler_con_ayuda = max(120.0, alquiler_efectivo - subv_monto)
        esfuerzo = (alquiler_con_ayuda + deudas) / ingresos

        z = 7.5 * (esfuerzo - 0.36)
        prob_viable = 1.0 / (1.0 + math.exp(z))
        if contrato == "Indefinido":
            prob_viable += 0.08
        else:
            prob_viable -= 0.06
        prob_viable = max(0.03, min(0.97, prob_viable))

        es_viable = 1 if random.random() < prob_viable else 0

        filas.append([
            sol_id, mun, edad_str, contrato,
            round(ingresos, 2), round(alquiler, 2), round(antiguedad, 1),
            ahorros_str, comparte, deudas,
            subv, es_viable
        ])

    return headers, filas

if __name__ == "__main__":
    headers, filas = generar_datos_csv(1200)
    base_dir = Path(__file__).resolve().parent.parent
    out_file = base_dir / "data" / "raw" / "solicitudes_vivienda_joven.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(filas)

    print(f"Dataset generado exitosamente en {out_file}: {len(filas)} filas.")
