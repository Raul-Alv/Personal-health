# Backend refactorizado

Este backend deja `main.py` como punto de arranque mínimo y reparte las responsabilidades así:

- `api/routes/`: define endpoints HTTP.
- `api/deps.py`: autenticación y autorización comunes.
- `services/`: procesos de negocio largos, como import y export.
- `repositories/`: acceso a RDF/SPARQL por recurso.
- `sparql/queries.py`: consultas centralizadas.
- `rdf_store.py`: apertura del store y grafos nombrados.
- `rdf_util.py`: utilidades RDF reutilizables.

## Flujo real

1. El router recibe la petición.
2. La dependencia valida el JWT y resuelve el usuario.
3. Si hace falta, otra dependencia comprueba vínculo usuario-paciente.
4. El router llama a un service o a un repository.
5. El repository ejecuta SPARQL sobre el grafo adecuado.
6. El router devuelve JSON o un fichero.

## Qué se ha conservado

- Los paths principales del backend original.
- El uso de JWT con `sub = URI del usuario`.
- El vínculo RDF `ex:tienePaciente` para autorización.
- La importación y exportación con RDF + ShEx.

## Qué sigue siendo mejorable

- Los borrados de procedimiento y alergia siguen siendo simples y no limpian blank nodes colgantes.
- Faltaría validar/sanitizar entradas que acaban dentro de queries SPARQL.
- Se podría añadir una capa de modelos Pydantic para respuestas.
