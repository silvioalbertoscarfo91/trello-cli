# Card description template (simple Spanish, Trello Markdown)

Short sentences, everyday Spanish ("español sencillo"), no Given/When/Then. One idea per bullet.
Technical names (endpoints, tables, screens) stay as they are, in `code`.
Acceptance criteria are NOT written here by hand: put them in `stories.json` (`ac`), the script inserts them
at `{{AC}}` and creates the checklist "Criterios de aceptación" with the same items.
Last criterion (optional): `Cubre: <parte del cambio 1>, <parte 2>`.

```
**Qué**
- <lo que se construye, 2-5 puntos concretos: pantalla, endpoint, tabla, tarea>

**Para quién**
<rol, p. ej. jugadores de la app | administradores | equipo de desarrollo>

**Por qué**
<una frase>

**Criterios de aceptación**
{{AC}}

**Dependencias**
Bloqueada por: {{BLOCKED_BY_LINKS}}
Bloquea: {{BLOCKS_LINKS}}

**Detalles técnicos**
Ver adjunto _{{ATTACHMENT}}_ (en inglés, para la implementación).
Todo cambio de código se entrega con una Pull Request (nunca directo a la rama principal).

**Referencias**
- [<título>](<url>)   (diseño, documento, ticket; quitar la sección si no hay)
```

`{{BLOCKED_BY_LINKS}}` / `{{BLOCKS_LINKS}}` become the card URLs, one per line (Trello shows a preview);
empty → `ninguna` (or `deps_text` from stories.json for the blocked-by line, e.g. "ninguna; se puede empezar
ya"). Both lines are ALWAYS written. `{{ATTACHMENT}}` becomes the attachment file name.
Other placeholders: `{{S07}}` card URL, `{{S07:link}}` `[title](url)`, `{{S07:title}}` title.
