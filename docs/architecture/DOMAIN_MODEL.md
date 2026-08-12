# Modelo de dominio

## Agregados

### Organización compradora

Raíz: `Organization`.

Contiene membresías, categorías, proveedores, plantillas y eventos. La primera
publicación soporta una organización por instalación en la experiencia guiada,
aunque el modelo mantiene aislamiento multi-organización para evitar un rediseño
posterior.

### Proveedor

Raíz: `Supplier`.

- Identidad fiscal única dentro de la organización compradora.
- Contactos y usuarios del portal.
- Categorías ofrecidas.
- Códigos externos por sistema y sociedad.
- Estados operativos separados del estado de homologación.

### Plantilla de homologación

Raíz: `QualificationTemplate`.

Una versión publicada no debe cambiar semánticamente. Las revisiones futuras
crean una nueva versión. Sus requisitos pueden ser generales o específicos de
una categoría.

### Expediente

Raíz: `QualificationCase`.

Congrega respuestas, documentos, revisiones y decisión. La máquina de estados
controla qué actor puede ejecutar cada acción. Un proveedor solo puede tener un
expediente abierto para la misma plantilla.

## Separación ERP

Supplier Hub es autoridad sobre homologación, documentos, evaluaciones y
decisiones. El ERP puede ser autoridad sobre códigos contables, sociedades,
materiales y bloqueos de pago. Los identificadores externos no reemplazan los
identificadores internos.

## Datos de IA futuros

Una `AISuggestion` almacenará salida estructurada, evidencia, confianza,
proveedor/modelo, versión de prompt y resolución humana. No sobrescribirá una
respuesta ni un documento.

