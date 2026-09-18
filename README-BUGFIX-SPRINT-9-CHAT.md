# Bugfix Sprint 9: diseño del chat

Corrige dos regresiones visuales:

1. Elimina el personaje insertado en el contenido principal de la página.
2. Utiliza una imagen oscurecida únicamente como fondo interno del panel del chat.
3. Restaura un botón X visible y accesible para cerrar el panel.
4. Mantiene la atribución Powered by Llama dentro del panel.
5. Oculta correctamente el panel cuando contiene el atributo hidden.

## Aplicación

Descomprime en la raíz del repositorio y ejecuta:

```powershell
python .\scripts\apply-chat-layout-bugfix.py
```

Después ejecuta Ruff, formato y pytest.
