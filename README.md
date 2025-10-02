# 🎯 Proyecto de Reconocimiento Facial

Este proyecto permite detectar y reconocer rostros desde la cámara web del usuario mediante una API en Python (Flask) y una interfaz web simple.

---

## 🚀 Instrucciones de instalación

### Backend

```bash
python -m venv venv
venv\Scripts\activate  # En Windows
pip install -r requirements.txt
python app.py
```

El servidor se ejecutará en `http://127.0.0.1:5000` o `http://localhost:5000`.

---

## 📱 Acceso desde dispositivos móviles

Para acceder desde un celular o tablet, la cámara requiere HTTPS. Usa ngrok para exponer el servidor con HTTPS.

### Instalar ngrok

1. Descarga ngrok desde [https://ngrok.com/download](https://ngrok.com/download).
2. Extrae el archivo y colócalo en una carpeta accesible desde la línea de comandos.
3. Regístrate en ngrok y obtén tu token de autenticación.
4. Ejecuta `ngrok config add-authtoken TU_TOKEN`.

### Ejecutar ngrok

Con el servidor Flask corriendo (`python app.py`), abre una nueva terminal y ejecuta:

```bash
ngrok http 5000
```

Ngrok te dará una URL HTTPS, por ejemplo: `https://unsapped-terminologically-vina.ngrok-free.dev`.

### Acceder desde el celular

1. Abre la URL HTTPS en tu navegador móvil (Chrome o Safari).
2. Asegúrate de que el navegador pida permisos para la cámara y concédelos.
   - En Android: Ajustes → Apps → Chrome → Permisos → Cámara → Permitir.
   - En iPhone: Ajustes → Safari → Cámara → Permitir.
3. La aplicación debería funcionar correctamente con la cámara.

### Notas importantes

- No uses `http://localhost:5000` en el celular; usa la URL de ngrok.
- Si hay errores de CORS, asegúrate de que el navegador esté usando HTTPS.
- Para monitorear las peticiones, abre `http://127.0.0.1:4040` en tu PC para ver el panel de ngrok.

---

## 🛠️ Desarrollo

- El frontend está en `frontend/`.
- Las rutas de la API están en `routes/`.
- Los modelos en `models/`.
- Base de datos en `instance/reconocimiento.db`.
