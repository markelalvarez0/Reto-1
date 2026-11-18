"""El mapa conserva el catálogo completo hasta que el usuario pide filtrarlo."""
import json
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_catalogue_map_is_independent_of_rent_selection(monkeypatch):
    evidence = ROOT / 'docs/evidencias_entrega_2026-11-12/municipal'
    monkeypatch.setenv('RETO1_ANALYSIS_DIR', str(evidence))
    expected = pd.DataFrame(json.loads((evidence / 'mapa_promociones.json').read_text()))
    app = AppTest.from_file(str(ROOT / 'app/territorio.py')).run(timeout=30)
    assert not app.exception
    pd.testing.assert_frame_equal(app.dataframe[1].value, expected)

    # Comparar únicamente Bilbao no debe ocultar promociones de otros municipios.
    app.multiselect[0].set_value(['Bilbao']).run()
    pd.testing.assert_frame_equal(app.dataframe[1].value, expected)
    assert 'Amurrio' in set(app.dataframe[1].value.municipio)

    app.checkbox(key='filtrar_mapa_municipios').check().run()
    pd.testing.assert_frame_equal(
        app.dataframe[1].value,
        expected.loc[expected.codigo_municipio == '48020'],
    )
    app.multiselect[0].set_value([]).run()
    assert app.dataframe[1].value.empty
    assert any('No hay promociones con coordenadas' in item.value for item in app.info)

    app.checkbox(key='filtrar_mapa_municipios').uncheck().run()
    assert not app.exception
    pd.testing.assert_frame_equal(app.dataframe[1].value, expected)
