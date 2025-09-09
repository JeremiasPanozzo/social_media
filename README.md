# 📸 Mini Red Social API

Una API REST construida con **Flask**, **SQLAlchemy** y **JWT** que permite manejar usuarios, posts con imágenes y comentarios.

## 🚀 Características

- Registro e inicio de sesión con **JWT**
- Subida de imágenes para posts
- Feed de publicaciones con autores
- Comentarios en posts
- Edición y eliminación de posts y usuarios
- Endpoints protegidos con autenticación

---

🔑 Autenticación 

- POST /auth/register → Registrar un nuevo usuario.
- POST /auth/login → Inicia sesión y devuelve el JWT.
- POST /auth/logout → Cerrar sesión (JWT blacklist)
- POST /auth/refresh → Refrescar token JWT

👨 Usuarios

- GET /users/me → Devuelve los datos del usuario autenticado (perfil propio).
- GET /users/<user_id> → Perfil de otro usuario (público, sin info sensible).
- PUT /users/me → Actualizar perfil propio.
- DELETE /users/me → Eliminar la cuenta.

📸 Posts

- POST /posts/upload_post → Crear post con imagen (form-data).
- GET /posts/feed → Feed general (todos los posts ordenados por fecha).
- GET /posts/<post_id> → Ver detalle de un post.
- DELETE /posts/<post_id> → Eliminar un post (solo el dueño).
- PUT /posts/<post_id> → Editar caption de un post (solo el dueño).

💬 Comentarios

- POST /posts/<post_id>/comments → Crear un comentario.
- GET /posts/<post_id>/comments → Listar comentarios de un post.
- DELETE /comments/<comment_id> → Borrar comentario (solo autor o admin).

  ## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/miniredsocial.git
cd miniredsocial
```

### 2. Crear un entorno virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
FLASK_SECRET_KEY=secret_key
FLASK_SQLALCHEMY_DATABASE_URI=sqlite:///social-network.db
FLASK_UPLOAD_FOLDER=uploads
```

### 5. Ejecutar servidor
```bash
flask run
```
