# TechSolutions VideoGames API

API REST desarrollada con **FastAPI + SQLAlchemy 2 + Pydantic 2 + SQLite** para gestionar un catálogo de videojuegos y sus categorías.

> Temática inicial: **Videojuegos / Categorías**. La estructura está preparada para adaptar la temática si el proyecto académico recibe otro visto bueno.

## 1. Arquitectura

```text
techsolutions_videojuegos_api/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── category.py
│   │   └── game.py
│   ├── schemas/
│   │   ├── category.py
│   │   └── game.py
│   ├── services/
│   │   ├── category_service.py
│   │   └── game_service.py
│   └── routers/
│       ├── categories.py
│       └── games.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   ├── conftest.py
│   ├── test_categories.py
│   └── test_games.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

La API utiliza una relación **1:N**:

- Una `Category` puede tener muchos `Game`.
- Cada `Game` pertenece a una única `Category`.
- `games.category_id` es una clave foránea hacia `categories.id`.

## 2. Tecnologías

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy 2
- SQLite
- Pydantic 2
- Pytest + HTTPX
- Axios
- HTML5 / CSS3 / JavaScript Vanilla

## 3. Instalación

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Copiar configuración:

```bash
copy .env.example .env
```

En Linux/macOS:

```bash
cp .env.example .env
```

## 4. Ejecutar

```bash
uvicorn app.main:app --reload
```

Abrir:

- Aplicación web: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

La base de datos SQLite se crea automáticamente al arrancar.

## 5. Endpoints

### Categorías

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/categories` | Lista categorías con paginación |
| GET | `/api/categories/{id}` | Obtiene una categoría y sus videojuegos |
| POST | `/api/categories` | Crea una categoría |
| PUT | `/api/categories/{id}` | Actualiza una categoría |
| DELETE | `/api/categories/{id}` | Elimina una categoría sin videojuegos |

### Videojuegos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/games` | Lista videojuegos con búsqueda, filtro y paginación |
| GET | `/api/games/{id}` | Obtiene un videojuego y su categoría |
| POST | `/api/games` | Crea un videojuego indicando `category_id` |
| PUT | `/api/games/{id}` | Actualiza un videojuego y su categoría |
| DELETE | `/api/games/{id}` | Elimina un videojuego |

## 6. Ejemplos

Crear categoría:

```http
POST /api/categories
Content-Type: application/json

{
  "name": "RPG",
  "description": "Juegos de rol y aventura."
}
```

Crear videojuego relacionado:

```http
POST /api/games
Content-Type: application/json

{
  "title": "The Witcher 3",
  "description": "RPG de mundo abierto.",
  "release_year": 2015,
  "developer": "CD Projekt Red",
  "platform": "PC",
  "category_id": 1
}
```

Filtrar videojuegos:

```text
GET /api/games?search=witcher&category_id=1&page=1&page_size=10
```

## 7. Códigos HTTP

- `200 OK`: lectura, actualización o eliminación correcta.
- `201 Created`: creación correcta.
- `400 Bad Request`: operación válida sintácticamente pero no permitida por las reglas de negocio.
- `404 Not Found`: recurso inexistente.
- `409 Conflict`: conflicto con la integridad referencial.
- `422 Unprocessable Entity`: error de validación de Pydantic/FastAPI.
- `500 Internal Server Error`: error inesperado del servidor.

## 8. Pruebas

```bash
pytest
```

## 9. Base de datos

Para desarrollo se utiliza SQLite:

```text
sqlite:///./techsolutions.db
```

En producción puede sustituirse por PostgreSQL configurando `DATABASE_URL`.

## 10. Gitflow sugerido

```text
main
└── develop
    ├── feature/backend
    ├── feature/frontend
    ├── feature/tests
    └── feature/documentation
```

## 11. Próximas mejoras académicas

Esta primera versión cubre el núcleo funcional. Para la entrega final se pueden añadir:

- autenticación/autorización si el profesor la solicita;
- migraciones con Alembic;
- PostgreSQL;
- N:M para géneros/plataformas;
- ordenación configurable;
- filtros adicionales;
- Docker;
- diagrama DER;
- diagrama de arquitectura;
- historias de usuario;
- Kanban;
- prototipo Figma/Stitch;
- más tests y cobertura;
- documentación más visual de endpoints.
