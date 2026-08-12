# Inteligencia artificial local

## Principios

- Supplier Hub funciona con la IA desactivada.
- El modo predeterminado usa reglas locales reproducibles y no hace red.
- Ollama es opcional y se comunica solamente con la URL configurada.
- Toda salida se almacena como propuesta pendiente con evidencia y confianza.
- Una persona acepta o rechaza; el modelo nunca homologa un proveedor.
- El texto del documento se trata como datos no confiables, no instrucciones.

## Modo local básico

`pypdf` extrae texto embebido y `RuleBasedProvider` reconoce inicialmente:

- identificación fiscal;
- fecha de vencimiento.

Este modo funciona en CPU y no descarga modelos. Un PDF escaneado requiere OCR.

## Ollama

Instala Ollama y un modelo cuya licencia sea compatible con tu uso. Supplier Hub
no descarga modelos automáticamente. Configura:

```text
SUPPLIER_HUB_AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:4b
```

El adaptador solicita JSON Schema y descarta cualquier propuesta cuyo campo no
esté permitido o cuya evidencia no aparezca literalmente en la página indicada.
La licencia de Ollama no reemplaza ni garantiza la licencia del modelo elegido.

## Docling y OCR

Existe un adaptador para Docling activable con:

```text
SUPPLIER_HUB_DOCUMENT_ENGINE=docling
```

Este perfil es opcional porque sus modelos y dependencias aumentan notablemente
el tamaño. Si Docling no está instalado, el sistema informa el requisito sin
afectar el núcleo. El empaquetado de OCR se cerrará antes de la primera release.

## Evaluaciones

```powershell
.\.venv\Scripts\python.exe manage.py evaluate_local_ai
```

El conjunto sintético comprueba valores, ausencia de falsos positivos y
normalización. Cada nuevo extractor o modelo debe tener un conjunto de
evaluación separado; no se aprobará por una demostración visual aislada.

