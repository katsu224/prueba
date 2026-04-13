# Sistema de Inventario con Kardex

## Descripción

Sistema de gestión de inventario con visualización de **Kardex** (registro histórico de movimientos de productos). Backend construido con FastAPI y PostgreSQL (Supabase).

## Tecnologías

| Componente | Tecnología |
|-----------|-----------|
| Backend | FastAPI (Python 3.12) |
| Base de datos | PostgreSQL (Supabase) |
| ORM | SQLAlchemy (async) |
| Autenticación | JWT (python-jose + bcrypt) |
| Frontend | React + Vite (próximamente) |

## Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py              # Entry point de la aplicación
│   ├── core/                # Configuración central
│   │   ├── config.py        # Variables de entorno
│   │   ├── database.py      # Conexión a BD
│   │   ├── exceptions.py    # Excepciones de dominio
│   │   └── security.py      # JWT y hashing
│   ├── models/              # Modelos ORM (SQLAlchemy)
│   ├── schemas/             # Schemas Pydantic (validación)
│   ├── repositories/        # Acceso a datos (queries)
│   ├── services/            # Lógica de negocio
│   └── api/v1/              # Endpoints de la API
├── tests/                   # Tests
├── .env.example             # Variables de entorno (ejemplo)
├── requirements.txt         # Dependencias Python
└── README.md                # Este archivo
```

## Arquitectura en Capas

```
Routes (API) → Services (Negocio) → Repositories (Datos) → Database
```

- **Routes**: Reciben peticiones HTTP, llaman al servicio
- **Services**: Lógica de negocio, validaciones, orquestación
- **Repositories**: Queries SQL/ORM, acceso a datos puro
- **Database**: Conexión y modelos

## Setup Rápido (Ubuntu)

```bash
# 1. Instalar dependencia del sistema
sudo apt install -y python3.12-venv

# 2. Crear entorno virtual y activarlo
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# 5. Ejecutar el servidor
uvicorn app.main:app --reload --port 8000
```

## Endpoints de la API

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| GET | `/api/v1/auth/me` | Perfil del usuario actual |

### Categorías
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/categories` | Listar categorías |
| POST | `/api/v1/categories` | Crear categoría |
| GET | `/api/v1/categories/{id}` | Obtener categoría |
| PUT | `/api/v1/categories/{id}` | Actualizar categoría |
| DELETE | `/api/v1/categories/{id}` | Eliminar categoría |

### Productos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/products` | Listar productos |
| POST | `/api/v1/products` | Crear producto |
| GET | `/api/v1/products/{id}` | Obtener producto |
| PUT | `/api/v1/products/{id}` | Actualizar producto |
| DELETE | `/api/v1/products/{id}` | Desactivar producto |

### Movimientos de Inventario
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/movements/types` | Tipos de movimiento |
| GET | `/api/v1/movements` | Listar movimientos |
| POST | `/api/v1/movements` | Registrar movimiento |
| GET | `/api/v1/movements/{id}` | Obtener movimiento |

### Kardex y Stock
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/kardex/{product_id}` | Kardex del producto |
| GET | `/api/v1/kardex/stock/{product_id}` | Stock de un producto |
| GET | `/api/v1/kardex/dashboard/stock` | Stock de todos |
| GET | `/api/v1/kardex/dashboard/low-stock` | Productos con stock bajo |

## Documentación Interactiva

Una vez ejecutando el servidor:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Licencia

MIT
