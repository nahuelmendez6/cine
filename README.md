# CineApp - Sistema de Gestión de Cine

CineApp es una aplicación web moderna para la gestión de cines, desarrollada con Django y React. Permite a los usuarios reservar entradas, gestionar películas y administrar salas de cine de manera eficiente.

## 🚀 Características

- Sistema de autenticación y autorización robusto
- Gestión de películas y salas de cine
- Sistema de reservas en tiempo real
- Procesamiento de pagos integrado
- Sistema de notificaciones
- Panel de administración personalizado
- API RESTful documentada
- Interfaz de usuario moderna y responsive

## 🛠️ Tecnologías Utilizadas

- **Backend:**
  - Django 4.2
  - Django REST Framework
  - MySQL
  - Celery & Redis
  - JWT Authentication

- **Frontend:**
  - React
  - Material-UI
  - Redux Toolkit
  - Axios

- **DevOps:**
  - Docker
  - GitHub Actions
  - AWS S3
  - Gunicorn

## 📋 Prerrequisitos

- Python 3.8+
- Node.js 14+
- MySQL 8.0+
- Redis

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/cine-app.git
cd cine-app
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Aplicar migraciones:
```bash
python manage.py migrate
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Iniciar el servidor de desarrollo:
```bash
python manage.py runserver
```

## 🧪 Tests

Ejecutar tests:
```bash
pytest
```

## 📚 Documentación

La documentación de la API está disponible en `/api/schema/` cuando el servidor está en ejecución.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- Tu Nombre - [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Django
- React
- Material-UI
- Y todos los demás proyectos open source que hacen esto posible 