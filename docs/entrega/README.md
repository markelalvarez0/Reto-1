# Entrega vigente del reto

Memorias con explicaciones sencillas, en primera persona del plural. Las presentaciones cuentan qué hicimos y por qué, con capturas reales, gráficos y esquemas. Los detalles técnicos quedan en las memorias y las respuestas de los guiones.

Los paquetes para entregar están en la raíz: [BDA/SBD](../../Entrega_BDA_SBD.zip) y [SAA/PIA/MIA](../../Entrega_SAA_PIA_MIA.zip). Incluyen memoria y presentación, código, datos y las instrucciones necesarias para cada bloque. Excluyen guiones orales, guía de defensa y revisión de rúbricas.

| Uso | PDF vigente | Fuente editable |
|---|---|---|
| Entrega BDA/SBD | [Documentación](BDA_SBD/Documentacion_BDA_SBD.pdf) | [Markdown](BDA_SBD/Documentacion_BDA_SBD.md) |
| Exposición BDA/SBD | [Presentación](BDA_SBD/Presentacion_BDA_SBD.pdf) | [Markdown](BDA_SBD/Presentacion_BDA_SBD.md) |
| Estudio BDA/SBD | [Guion oral](BDA_SBD/Guion_oral_BDA_SBD.pdf) | [Markdown](BDA_SBD/Guion_oral_BDA_SBD.md) |
| Entrega SAA/PIA/MIA | [Documentación](SAA_PIA_MIA/Documentacion_SAA_PIA_MIA.pdf) | [Markdown](SAA_PIA_MIA/Documentacion_SAA_PIA_MIA.md) |
| Exposición IA, 15 minutos | [Presentación](SAA_PIA_MIA/Presentacion_SAA_PIA_MIA.pdf) | [Markdown](SAA_PIA_MIA/Presentacion_SAA_PIA_MIA.md) |
| Estudio IA | [Guion oral](SAA_PIA_MIA/Guion_oral_SAA_PIA_MIA.pdf) | [Markdown](SAA_PIA_MIA/Guion_oral_SAA_PIA_MIA.md) |
| Entrega y estudio común | [Guía](Guia_entrega_y_defensa.pdf) | [Markdown](Guia_entrega_y_defensa.md) |
| Comprobación adicional | [Revisión de rúbricas](Revision_rubricas.pdf) | [Markdown](Revision_rubricas.md) |

La revisión usa los dos PDF docentes adjuntos en el chat. Sus nombres, páginas y huellas están en la revisión y el manifiesto de validación; no se redistribuyen los enunciados originales. **No es una certificación de nota.** La demostración BDA/SBD, los datos en servicios, las preguntas individuales y la valoración docente no se sustituyen por estos archivos.

## Qué conservamos como histórico

Los cuatro informes PDF de raíz y carpetas académicas tienen exactamente el mismo contenido, verificado por SHA-256. Se conservan para no romper referencias ni borrar evidencia: `Entrega_Reto1_IABD_Documentacion.pdf`, `DOCUMENTO_MAESTRO_CONTEXTO_TECNICO_RETO1.pdf` y sus dos copias de bloque. El hash es `629956f7a3fa836d0fb12d42d4e7e05d1f3e264ffeaac86da242529371f99e5b`.

`docs/guia_defensa/` conserva el manual, Word, guía rápida, presentaciones y ZIP anteriores. Las presentaciones y guiones vigentes son los de esta carpeta. Los apartados históricos de `CONTINUAR.md` y `ESTADO_ENTREGA.md` no vuelven a abrir tareas técnicas resueltas después.

La captura antigua de MLflow mostraba la interfaz cargando. La nueva captura de `assets/mlflow_experimentos_2026-11-17.png` muestra la tabla abierta sobre una copia de los registros históricos. No cambia los experimentos originales. Las figuras se dibujan desde train, CSV de validación y resultados municipales conservados. Las cuatro capturas nuevas muestran el visor, el mapa y un caso ficticio de la app. Su procedencia está en `assets/procedencia_visuales.json`. Las capturas de inferencia no reentrenan ni vuelven a puntuar el test.

## Regeneración

`scripts/build_academic_docs.py` necesita `requirements-documentacion.txt`, preferiblemente en un entorno separado. Lee Markdown e imágenes y genera PDF reales con texto seleccionable, índice, páginas y gráficos. No importa módulos ML ni carga joblib. `scripts/build_academic_figures.py` usa matplotlib del entorno del proyecto para dibujar las figuras de presentación a partir de CSV conservados.

La captura MLflow es una captura de navegador de la aplicación real y no la dibuja el generador. Para repetirla se abre una copia de la base SQLite y se espera a que aparezca la tabla con los once experimentos. Las métricas de entrenamiento se distinguen de la duración total que muestra la interfaz.

`manifest_documentos.json` relaciona PDF y fuentes con SHA-256. `validacion_documentacion.json` registra las comprobaciones actuales, la integridad y las diferencias entre ejecución nueva y evidencia histórica. Las pruebas no sustituyen el ensayo oral de la pareja.

Los ZIP se generan con `python scripts/build_delivery_packages.py`. Cada paquete incluye un inventario con huellas y su comprobador, y se valida después de extraerlo en una carpeta nueva.
