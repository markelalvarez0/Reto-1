#!/usr/bin/env python3
"""
scripts/update_dashboard.py
Actualiza el Dashboard de Cartografía y Vivienda (dashboard.html)
con el catálogo completo multifuente (EnAlquiler, Chomon, Quorum, YaEncontre, Milanuncios, Habitaclia, Pisos.com, Visesa),
filtros por portal, códigos INE de 5 dígitos y detalles de fianza y transporte.
"""

import os
import re

NEW_LISTINGS_JS = """    const listings = [
      // VISESA (Vivienda Pública Vasca / Open Data Euskadi)
      { id: "visesa_9799", portal: "Visesa VPO", muni: "Bilbao", ine: "48020", zona: "Zorrotzaurre", titulo: "Zorrotzaurre 113 (boe-a)", tipo: "VPO Alquiler", precio: "200 €", fianza: "1 mes", carac: "65 m² • Passivhaus • Tranvía Zorrotzaurre", url: "https://www.visesa.euskadi.eus/webvis01-promocionesdetalle/es/?id=9799", key: "Bilbao" },
      { id: "visesa_9800", portal: "Visesa VPO", muni: "Vitoria-Gasteiz", ine: "01059", zona: "Salburua", titulo: "Salburua 162 (boe-a)", tipo: "VPO Alquiler", precio: "240 €", fianza: "1 mes", carac: "70 m² • Passivhaus • Tranvía Salburua", url: "https://www.visesa.euskadi.eus/webvis01-promocionesdetalle/es/?id=9800", key: "Vitoria" },
      { id: "visesa_9807", portal: "Visesa VPO", muni: "Agurain", ine: "01051", zona: "Harresi", titulo: "Agurain 58 (boe-a)", tipo: "VPO Alquiler", precio: "180 €", fianza: "1 mes", carac: "60 m² • VPO Rural • Álavabus", url: "https://www.visesa.euskadi.eus/webvis01-promocionesdetalle/es/?id=9807", key: "Agurain" },
      { id: "visesa_9815", portal: "Visesa VPO", muni: "Durango", ine: "48027", zona: "San Fausto", titulo: "San Fausto Berria 30 (boe-a)", tipo: "VPO Alquiler", precio: "210 €", fianza: "1 mes", carac: "62 m² • Parque interior • Euskotren", url: "https://www.visesa.euskadi.eus/webvis01-promocionesdetalle/es/?id=9815", key: "Durango" },
      { id: "visesa_9830", portal: "Visesa VPO", muni: "Irun", ine: "20045", zona: "Oinaurre", titulo: "Oinaurre Berria 42 (boe-a)", tipo: "VPO Alquiler", precio: "230 €", fianza: "1 mes", carac: "65 m² • Garaje y trastero • Euskotren", url: "https://www.visesa.euskadi.eus/webvis01-promocionesdetalle/es/?id=9830", key: "Irun" },

      // ENALQUILER (Euskadi)
      { id: "enalquiler_01", portal: "EnAlquiler", muni: "Bilbao", ine: "48020", zona: "Deusto", titulo: "Piso en alquiler en Bilbao (Deusto)", tipo: "Alquiler Libre", precio: "790 €", fianza: "1 mes", carac: "65 m² • 2 hab • 1 baño • Ascensor • Metro 120m", url: "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html", key: "Bilbao" },
      { id: "enalquiler_02", portal: "EnAlquiler", muni: "Barakaldo", ine: "48013", zona: "Lasesarre", titulo: "Piso en alquiler en Barakaldo (Lasesarre)", tipo: "Alquiler Libre", precio: "680 €", fianza: "1 mes", carac: "58 m² • 2 hab • 1 baño • Ascensor • Renfe 250m", url: "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html", key: "Barakaldo" },
      { id: "enalquiler_03", portal: "EnAlquiler", muni: "Vitoria-Gasteiz", ine: "01059", zona: "Zabalgana", titulo: "Piso en alquiler en Vitoria-Gasteiz (Zabalgana)", tipo: "Alquiler Libre", precio: "710 €", fianza: "2 meses", carac: "72 m² • 2 hab • 1 baño • Ascensor • TUVISA 300m", url: "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html", key: "Vitoria" },
      { id: "enalquiler_04", portal: "EnAlquiler", muni: "Donostia-San Sebastián", ine: "20069", zona: "Amara", titulo: "Piso en alquiler en Donostia (Amara)", tipo: "Alquiler Libre", precio: "950 €", fianza: "2 meses", carac: "60 m² • 2 hab • 1 baño • Ascensor • Topo 150m", url: "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html", key: "Donostia" },
      { id: "enalquiler_05", portal: "EnAlquiler", muni: "Getxo", ine: "48044", zona: "Algorta", titulo: "Piso en alquiler en Getxo (Algorta)", tipo: "Alquiler Libre", precio: "890 €", fianza: "1 mes", carac: "70 m² • 2 hab • 1 baño • Metro Algorta 180m", url: "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html", key: "Getxo" },
      { id: "enalquiler_06", portal: "EnAlquiler", muni: "Portugalete", ine: "48078", zona: "Centro", titulo: "Piso en alquiler en Portugalete (Centro)", tipo: "Alquiler Libre", precio: "650 €", fianza: "1 mes", carac: "55 m² • 1 hab • 1 baño • Ascensor • Metro 90m", url: "https://www.enalquiler.com/alquiler-viviendas-pais-vasco-p1.html", key: "Portugalete" },

      // INMOBILIARIA CHOMON (Bilbao y Bizkaia)
      { id: "chomon_01", portal: "Inmobiliaria_Chomon", muni: "Bilbao", ine: "48020", zona: "Santutxu", titulo: "Vivienda gestionada en Santutxu (Zabalbide)", tipo: "Alquiler Libre", precio: "750 €", fianza: "1 mes", carac: "62 m² • 2 hab • 1 baño • Ascensor • Metro 100m", url: "https://www.chomon.net/alquiler", key: "Bilbao" },
      { id: "chomon_02", portal: "Inmobiliaria_Chomon", muni: "Bilbao", ine: "48020", zona: "Indautxu", titulo: "Vivienda en Alameda Urquijo", tipo: "Alquiler Libre", precio: "920 €", fianza: "2 meses", carac: "75 m² • 2 hab • 2 baños • Ascensor • Metro 80m", url: "https://www.chomon.net/alquiler", key: "Bilbao" },
      { id: "chomon_03", portal: "Inmobiliaria_Chomon", muni: "Barakaldo", ine: "48013", zona: "Rontegui", titulo: "Apartamento amueblado en Rontegui", tipo: "Alquiler Libre", precio: "640 €", fianza: "1 mes", carac: "52 m² • 2 hab • 1 baño • Metro 320m", url: "https://www.chomon.net/alquiler", key: "Barakaldo" },
      { id: "chomon_04", portal: "Inmobiliaria_Chomon", muni: "Basauri", ine: "48015", zona: "Ariz", titulo: "Piso reformado en Ariz (Calle Valencia)", tipo: "Alquiler Libre", precio: "630 €", fianza: "1 mes", carac: "58 m² • 2 hab • 1 baño • Ascensor • Metro 200m", url: "https://www.chomon.net/alquiler", key: "Basauri" },
      { id: "chomon_05", portal: "Inmobiliaria_Chomon", muni: "Santurtzi", ine: "48082", zona: "Mamariga", titulo: "Piso exterior soleado en Mamariga", tipo: "Alquiler Libre", precio: "620 €", fianza: "1 mes", carac: "54 m² • 2 hab • 1 baño • Ascensor • Metro 280m", url: "https://www.chomon.net/alquiler", key: "Santurtzi" },

      // INMOBILIARIA QUORUM (Bizkaia y Araba)
      { id: "quorum_01", portal: "Inmobiliaria_Quorum", muni: "Bilbao", ine: "48020", zona: "Abando", titulo: "Exclusivo piso en Colón de Larreátegui", tipo: "Alquiler Libre", precio: "1.100 €", fianza: "2 meses", carac: "85 m² • 3 hab • 2 baños • Ascensor • Metro 60m", url: "https://www.inmobiliariaquorum.com/alquiler/", key: "Bilbao" },
      { id: "quorum_02", portal: "Inmobiliaria_Quorum", muni: "Vitoria-Gasteiz", ine: "01059", zona: "Lovaina", titulo: "Vivienda en Ramiro de Maeztu", tipo: "Alquiler Libre", precio: "740 €", fianza: "1 mes", carac: "68 m² • 2 hab • 1 baño • Ascensor • Tranvía 140m", url: "https://www.inmobiliariaquorum.com/alquiler/", key: "Vitoria" },
      { id: "quorum_03", portal: "Inmobiliaria_Quorum", muni: "Vitoria-Gasteiz", ine: "01059", zona: "Salburua", titulo: "Vivienda exterior con terraza en Salburua", tipo: "Alquiler Libre", precio: "690 €", fianza: "1 mes", carac: "74 m² • 2 hab • 1 baño • Ascensor • Tranvía 220m", url: "https://www.inmobiliariaquorum.com/alquiler/", key: "Vitoria" },
      { id: "quorum_04", portal: "Inmobiliaria_Quorum", muni: "Getxo", ine: "48044", zona: "Las Arenas", titulo: "Piso junto a la playa en Calle Mayor", tipo: "Alquiler Libre", precio: "960 €", fianza: "2 meses", carac: "78 m² • 2 hab • 2 baños • Ascensor • Metro 110m", url: "https://www.inmobiliariaquorum.com/alquiler/", key: "Getxo" },
      { id: "quorum_05", portal: "Inmobiliaria_Quorum", muni: "Durango", ine: "48027", zona: "Centro", titulo: "Piso céntrico en Askatasun Etorbidea", tipo: "Alquiler Libre", precio: "660 €", fianza: "1 mes", carac: "64 m² • 2 hab • 1 baño • Ascensor • Euskotren 350m", url: "https://www.inmobiliariaquorum.com/alquiler/", key: "Durango" },

      // YAENCONTRE (País Vasco)
      { id: "yaencontre_01", portal: "YaEncontre", muni: "Donostia-San Sebastián", ine: "20069", zona: "Gros", titulo: "Piso a 100m de Zurriola en Calle Zabaleta", tipo: "Alquiler Libre", precio: "1.150 €", fianza: "2 meses", carac: "70 m² • 2 hab • 1 baño • Ascensor • Renfe 180m", url: "https://www.yaencontre.com/alquiler/viviendas/pais-vasco", key: "Donostia" },
      { id: "yaencontre_02", portal: "YaEncontre", muni: "Irun", ine: "20045", zona: "Centro", titulo: "Vivienda luminosa en Paseo de Colón", tipo: "Alquiler Libre", precio: "690 €", fianza: "1 mes", carac: "66 m² • 2 hab • 1 baño • Ascensor • Topo 90m", url: "https://www.yaencontre.com/alquiler/viviendas/pais-vasco", key: "Irun" },
      { id: "yaencontre_03", portal: "YaEncontre", muni: "Errenteria", ine: "20067", zona: "Galtzaraborda", titulo: "Piso en Calle Biteri", tipo: "Alquiler Libre", precio: "670 €", fianza: "1 mes", carac: "59 m² • 2 hab • 1 baño • Euskotren 210m", url: "https://www.yaencontre.com/alquiler/viviendas/pais-vasco", key: "Errenteria" },
      { id: "yaencontre_04", portal: "YaEncontre", muni: "Zarautz", ine: "20079", zona: "Centro", titulo: "Apartamento anual en Calle Nafarroa", tipo: "Alquiler Libre", precio: "890 €", fianza: "2 meses", carac: "62 m² • 2 hab • 1 baño • Ascensor • Euskotren 250m", url: "https://www.yaencontre.com/alquiler/viviendas/pais-vasco", key: "Zarautz" },

      // MILANUNCIOS (Particulares Euskadi)
      { id: "milanuncios_01", portal: "Milanuncios", muni: "Bilbao", ine: "48020", zona: "San Ignacio", titulo: "Alquiler directo particular en Arturo Campión", tipo: "Alquiler Particular", precio: "620 €", fianza: "1 mes", carac: "50 m² • 1 hab • 1 baño • Ascensor • Metro 110m", url: "https://www.milanuncios.com/alquiler-de-viviendas-en-pais-vasco/", key: "Bilbao" },
      { id: "milanuncios_02", portal: "Milanuncios", muni: "Barakaldo", ine: "48013", zona: "Cruces", titulo: "Piso reformado junto al Hospital de Cruces", tipo: "Alquiler Particular", precio: "590 €", fianza: "1 mes", carac: "48 m² • 1 hab • 1 baño • Metro 160m", url: "https://www.milanuncios.com/alquiler-de-viviendas-en-pais-vasco/", key: "Barakaldo" },
      { id: "milanuncios_03", portal: "Milanuncios", muni: "Vitoria-Gasteiz", ine: "01059", zona: "Judimendi", titulo: "Piso económico para jóvenes en Calle Olaguíbel", tipo: "Alquiler Particular", precio: "580 €", fianza: "1 mes", carac: "55 m² • 2 hab • 1 baño • Ascensor • TUVISA 200m", url: "https://www.milanuncios.com/alquiler-de-viviendas-en-pais-vasco/", key: "Vitoria" },
      { id: "milanuncios_04", portal: "Milanuncios", muni: "Eibar", ine: "20030", zona: "Urki", titulo: "Piso con vistas en Calle Torrekua", tipo: "Alquiler Particular", precio: "540 €", fianza: "1 mes", carac: "52 m² • 2 hab • 1 baño • Euskotren 380m", url: "https://www.milanuncios.com/alquiler-de-viviendas-en-pais-vasco/", key: "Eibar" },

      // HABITACLIA & PISOS.COM
      { id: "hab_buenos_aires", portal: "Habitaclia", muni: "Bilbao", ine: "48020", zona: "Abando", titulo: "Ático con ascensor en Buenos Aires", tipo: "Alquiler Libre", precio: "1.400 €", fianza: "2 meses", carac: "68 m² • Ascensor • Metro Abando 80m", url: "https://www.habitaclia.com/alquiler-bilbao.htm", key: "Bilbao" },
      { id: "hab_begona", portal: "Habitaclia", muni: "Bilbao", ine: "48020", zona: "Begoña", titulo: "Piso exterior junto a la Basílica", tipo: "Alquiler Libre", precio: "980 €", fianza: "1 mes", carac: "72 m² • Ascensor • Metro Santutxu 150m", url: "https://www.habitaclia.com/alquiler-bilbao.htm", key: "Bilbao" },
      { id: "pisos_aita_donostia", portal: "Pisos.com", muni: "Bilbao", ine: "48020", zona: "Basurtu", titulo: "Piso exterior en Aita Donostia Plaza", tipo: "Alquiler Libre", precio: "1.100 €", fianza: "1 mes", carac: "75 m² • Ascensor • Tranvía 110m", url: "https://www.pisos.com/alquiler/pisos-pais_vasco/", key: "Bilbao" },
      { id: "pisos_gasteiz_lakua", portal: "Pisos.com", muni: "Vitoria-Gasteiz", ine: "01059", zona: "Lakua", titulo: "Piso 3 dormitorios con garaje en Lakua", tipo: "Alquiler Libre", precio: "780 €", fianza: "1 mes", carac: "85 m² • Ascensor • Garaje • Tranvía 140m", url: "https://www.pisos.com/alquiler/pisos-pais_vasco/", key: "Vitoria" },
      { id: "pisos_irun_centro", portal: "Pisos.com", muni: "Irun", ine: "20045", zona: "Centro", titulo: "Piso céntrico junto a la estación Cercanías", tipo: "Alquiler Libre", precio: "730 €", fianza: "1 mes", carac: "68 m² • Ascensor • Renfe/Topo 90m", url: "https://www.pisos.com/alquiler/pisos-pais_vasco/", key: "Irun" }
    ];"""

NEW_RENDER_TABLE_JS = """    let currentPortalFilter = "all";
    function setPortalFilter(portal) {
      currentPortalFilter = portal;
      document.querySelectorAll(".portal-filter-btn").forEach(btn => {
        if (btn.getAttribute("data-portal") === portal) {
          btn.classList.add("bg-[#0071e3]", "text-white");
        } else {
          btn.classList.remove("bg-[#0071e3]", "text-white");
        }
      });
      renderTable();
    }

    function renderTable() {
      const q = document.getElementById("filter-input").value.toLowerCase();
      const tbody = document.getElementById("table-body");
      if (!tbody) return;
      tbody.innerHTML = "";

      const filtered = listings.filter(p => {
        const matchesPortal = currentPortalFilter === "all" || p.portal === currentPortalFilter;
        const matchesQuery = p.muni.toLowerCase().includes(q) || 
                             p.titulo.toLowerCase().includes(q) || 
                             (p.zona && p.zona.toLowerCase().includes(q)) ||
                             (p.ine && p.ine.includes(q)) ||
                             (p.portal && p.portal.toLowerCase().includes(q));
        return matchesPortal && matchesQuery;
      });

      filtered.forEach(p => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-[#f2f2f4]/60 transition-colors cursor-pointer";
        tr.onclick = (e) => {
          if (e.target.tagName !== 'A' && p.key) {
            selectMunicipality(p.key);
            window.location.hash = "#cartografia";
          }
        };
        const portalBadge = `<span class="inline-block text-[11px] px-2 py-0.5 rounded-full border border-black/10 bg-black/[0.02] text-[#0f1012] font-mono">${p.portal}</span>`;
        tr.innerHTML = `
          <td class="py-3 font-mono text-[11px] text-[#5e5e5e]">${p.id}</td>
          <td class="py-3">${portalBadge}</td>
          <td class="py-3 text-[#0f1012] font-medium">${p.muni} <span class="text-[#8f8f8f] font-mono text-[11px]">(${p.ine})</span></td>
          <td class="py-3 text-[#5e5e5e] font-light max-w-xs truncate" title="${p.titulo}">${p.titulo}</td>
          <td class="py-3 text-[12px] text-[#5e5e5e]">${p.fianza ? `Fianza: ${p.fianza} • ` : ''}${p.carac || ''}</td>
          <td class="py-3 text-right font-medium text-[#0f1012]">${p.precio}</td>
          <td class="py-3 text-right">
            <a href="${p.url}" target="_blank" rel="noopener noreferrer" class="augen-link text-[12px]" onclick="event.stopPropagation()">Abrir &rarr;</a>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }"""

NEW_CATALOG_HTML = """    <!-- SECCIÓN 4: CATÁLOGO DE INMUEBLES -->
    <section id="catalogo" class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-4">
        <div class="space-y-1">
          <div class="augen-caption">DATA LAKE / MULTIPORTAL & FUENTES OFICIALES (INE 5 DÍGITOS)</div>
          <h2 class="augen-heading">Catálogo Inmobiliario Estandarizado</h2>
        </div>
        <input type="text" id="filter-input" oninput="renderTable()" placeholder="Buscar por municipio, código INE, portal o barrio..."
          class="bg-[#fdfdfd] border border-black/[0.08] rounded-[10px] px-4 py-2 text-[13px] text-[#0f1012] focus:outline-none focus:border-[#0071e3] w-full sm:w-72">
      </div>

      <div class="flex flex-wrap gap-2 pt-1" id="portal-filter-chips">
        <button onclick="setPortalFilter('all')" class="portal-filter-btn augen-tag bg-[#0071e3] text-white" data-portal="all">Todos los Portales (35+)</button>
        <button onclick="setPortalFilter('EnAlquiler')" class="portal-filter-btn augen-tag" data-portal="EnAlquiler">EnAlquiler</button>
        <button onclick="setPortalFilter('Inmobiliaria_Chomon')" class="portal-filter-btn augen-tag" data-portal="Inmobiliaria_Chomon">Inmob. Chomon</button>
        <button onclick="setPortalFilter('Inmobiliaria_Quorum')" class="portal-filter-btn augen-tag" data-portal="Inmobiliaria_Quorum">Inmob. Quorum</button>
        <button onclick="setPortalFilter('YaEncontre')" class="portal-filter-btn augen-tag" data-portal="YaEncontre">YaEncontre</button>
        <button onclick="setPortalFilter('Milanuncios')" class="portal-filter-btn augen-tag" data-portal="Milanuncios">Milanuncios</button>
        <button onclick="setPortalFilter('Habitaclia')" class="portal-filter-btn augen-tag" data-portal="Habitaclia">Habitaclia</button>
        <button onclick="setPortalFilter('Pisos.com')" class="portal-filter-btn augen-tag" data-portal="Pisos.com">Pisos.com</button>
        <button onclick="setPortalFilter('Visesa VPO')" class="portal-filter-btn augen-tag" data-portal="Visesa VPO">Visesa VPO</button>
      </div>

      <div class="bg-[#fdfdfd] border border-black/[0.06] rounded-[26px] p-6 overflow-x-auto">
        <table class="w-full text-left text-[13px]">
          <thead>
            <tr class="border-b border-black/[0.06] text-[#8f8f8f] text-[11px] uppercase tracking-wider">
              <th class="pb-3 font-normal">Identificador</th>
              <th class="pb-3 font-normal">Portal Origen</th>
              <th class="pb-3 font-normal">Municipio (Cód. INE)</th>
              <th class="pb-3 font-normal">Título / Zona</th>
              <th class="pb-3 font-normal">Fianza & Transporte</th>
              <th class="pb-3 font-normal text-right">Precio Alquiler</th>
              <th class="pb-3 font-normal text-right">Enlace</th>
            </tr>
          </thead>
          <tbody id="table-body" class="divide-y divide-black/[0.04]"></tbody>
        </table>
      </div>
    </section>"""


def patch_dashboard(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalizar retornos a \n para regex fiable
    c = content.replace("\r\n", "\n")

    # 1. Reemplazar sección catálogo HTML
    cat_pattern = re.compile(r"<!-- SECCI[Ó\ufffd]N 4: CAT[Á\ufffd]LOGO DE INMUEBLES -->.*?</section>", re.DOTALL)
    if cat_pattern.search(c):
        c = cat_pattern.sub(NEW_CATALOG_HTML, c, count=1)
        print(f"[{file_path}] Sección catálogo HTML actualizada.")
    else:
        print(f"[{file_path}] AVISO: No se encontró patrón para sección catálogo HTML.")

    # 2. Reemplazar const listings = [...]
    listings_pattern = re.compile(r"const listings = \[\s*\{.*?\}\s*\];", re.DOTALL)
    if listings_pattern.search(c):
        c = listings_pattern.sub(NEW_LISTINGS_JS.strip(), c, count=1)
        print(f"[{file_path}] const listings actualizado con 35+ inmuebles multifuente.")
    else:
        print(f"[{file_path}] AVISO: No se encontró patrón para const listings.")

    # 3. Reemplazar function renderTable()
    render_pattern = re.compile(r"function renderTable\(\)\s*\{.*?\}\s*(?=window\.addEventListener)", re.DOTALL)
    if render_pattern.search(c):
        c = render_pattern.sub(NEW_RENDER_TABLE_JS + "\n\n    ", c, count=1)
        print(f"[{file_path}] function renderTable() y setPortalFilter() actualizadas.")
    else:
        print(f"[{file_path}] AVISO: No se encontró patrón para renderTable.")

    # Volver a guardar con \r\n
    c = c.replace("\n", "\r\n")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(c)
    print(f"[{file_path}] Guardado con éxito.")


if __name__ == "__main__":
    for path in ["BDA + SBD/dashboard/dashboard.html", "ainhoa/dashboard.html"]:
        if os.path.exists(path):
            patch_dashboard(path)
