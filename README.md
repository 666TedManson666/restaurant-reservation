# MesaReserva – Sistema de Reservas de Restaurante

Sistema completo de reservas para restaurante con **Django + DRF + PostgreSQL** (backend) y **Vue 3 + Vite + Pinia** (frontend).

---

## 🚀 Quickstart Local

### Requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (o SQLite para dev)

### Backend

```bash
cd restaurant-backend

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env con tu DATABASE_URL (deja SQLite por defecto para dev)

# 3. Migraciones
python manage.py migrate

# 4. Crear superusuario admin
python manage.py seed_data
# o manualmente:
python manage.py createsuperuser

# 5. Correr servidor
python manage.py runserver
```

Backend disponible en: `http://localhost:8000`

### Frontend

```bash
cd restaurant-frontend

# 1. Instalar dependencias
npm install

# 2. Configurar variable de entorno
cp .env.example .env
# VITE_API_URL=http://localhost:8000/api

# 3. Servidor de desarrollo
npm run dev
```

Frontend disponible en: `http://localhost:5173`

---

## 🔑 Variables de Entorno

### Backend (`.env`)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Modo debug | `True` / `False` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,myapp.com` |
| `DATABASE_URL` | URL de conexión DB | `postgres://user:pass@host:5432/db` |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS (separados por coma) | `https://myfrontend.com` |

### Frontend (`.env`)

| Variable | Descripción |
|---|---|
| `VITE_API_URL` | URL base del backend API |

---

## 📦 Despliegue en Producción

### Backend (Render / Railway)

1. Crear servicio Web con Python
2. Comando de build: `pip install -r requirements.txt`
3. Comando de inicio: `gunicorn config.wsgi:application`
4. Variables de entorno:
   ```
   SECRET_KEY=<generar_clave_segura>
   DEBUG=False
   DATABASE_URL=<url_postgres_gestionado>
   ALLOWED_HOSTS=<tu-dominio.com>
   CORS_ALLOWED_ORIGINS=https://<tu-frontend.vercel.app>
   ```
5. Correr migraciones: `python manage.py migrate`

### Frontend (Vercel / Netlify)

1. Conectar repositorio
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Variable de entorno: `VITE_API_URL=https://<tu-backend>/api`

### Base de datos PostgreSQL

- Usar PostgreSQL gestionado: Render, Neon, Supabase, Railway
- La `DATABASE_URL` se inyecta como variable de entorno

---

## 🔌 API Endpoints

### Públicos
| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/availability/?date=YYYY-MM-DD&guests=N` | Consultar turnos disponibles |
| `POST` | `/api/reservations/` | Crear reserva |
| `POST` | `/api/reservations/cancel/` | Cancelar con `cancel_code` |

### Admin (JWT requerido)
| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/auth/token/` | Obtener JWT |
| `GET/POST` | `/api/admin/tables/` | CRUD mesas |
| `GET/PATCH` | `/api/admin/schedule/` | Horario |
| `GET` | `/api/admin/reservations/` | Listar reservas |
| `POST` | `/api/admin/reservations/{id}/cancel/` | Cancelar reserva |
| `GET` | `/api/admin/metrics/?date=YYYY-MM-DD` | Métricas de ocupación |

---

## 🧪 Tests

```bash
cd restaurant-backend
python manage.py test reservations -v 2
```

Cubre: disponibilidad, capacidad insuficiente, fechas pasadas, horario inválido, sobre-reserva, cancelación, métricas.

---

## 👤 Usuario Admin Demo

```
Usuario: admin
Contraseña: Admin1234!
```
*(Creado con `python manage.py seed_data`)*

---

## 🏗 Arquitectura

```
restaurant-reservation/
├── restaurant-backend/        # Django + DRF + PostgreSQL
│   ├── config/                # Settings, URLs
│   └── reservations/          # App principal
│       ├── models.py          # Table, RestaurantSchedule, Reservation
│       ├── services.py        # Lógica de negocio + select_for_update()
│       ├── serializers.py     # Validación de datos
│       ├── views.py           # Endpoints API
│       └── tests.py           # 21 tests unitarios
│
└── restaurant-frontend/       # Vue 3 + Vite + Pinia
    └── src/
        ├── api/               # Axios + interceptores JWT
        ├── stores/            # Pinia (auth)
        ├── router/            # Vue Router + guards
        └── views/             # Home, Confirmation, Cancel, Admin
```
