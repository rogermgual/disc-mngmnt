# Discord Management Python Bot
Bot de Discord basado en Python con comandos slash.

## Qué funciona hoy
### Comandos disponibles
- `/ping` – comprueba que el bot responde.
- `/birthday_add <day> <month>` – registra o actualiza el cumpleaños propio en formato DD/MM.
- `/birthday_remove` – elimina el cumpleaños propio si existe.
- `/birthday_week` – muestra los cumpleaños próximos en los siguientes 7 días.
- `/birthday_check_all` – lista todos los cumpleaños registrados.
- `/birthday_check <username>` – busca el cumpleaños de un usuario por nombre.
- `/birthday_announce_upcoming` – dispara manualmente el anuncio de próximos cumpleaños.
- `/birthday_announce_today` – dispara manualmente el anuncio de cumpleaños del día.

### Comportamiento automático
- El bot ejecuta dos jobs automáticos a las `09:00` (hora de Madrid):
  - anuncio de próximos cumpleaños en los siguientes 7 días,
  - anuncio de los cumpleaños del día.
- Los mensajes automáticos se envían al canal configurado en `SERVER_UPDATES_CHANNEL_ID`.

### Mensajes generados
- Próximos cumpleaños:
  - `Kweh! Cumpleaños a la vista 👀 de **<usuario>**`
- Cumpleaños del día:
  - `Kweh! Kweh! @everyone felicitad a <@usuario> 🎉🥳`

## Estructura y rutas de producción
Este proyecto está preparado para ejecutarse desde:

- código: `/opt/discord-bot/disc-mngmnt`
- base de datos SQLite: `/opt/discord-bot/data/bot.db`
- logs de errores: `/opt/discord-bot/logs/errors.log`
- entorno virtual: `/opt/discord-bot/venv`

El bot se ejecuta como el usuario `discord-bot` mediante `systemd`.

## Configuración necesaria
Copia o ajusta el archivo `.env` con estos valores:

```env
DISCORD_TOKEN=tu_token_aqui
SERVER_UPDATES_CHANNEL_ID=123456789012345678
DB_PATH=/opt/discord-bot/data/bot.db
DB_NAME=bot
LOG_DIR=/opt/discord-bot/logs
TZ=Europe/Madrid
```

### Qué cambiar para tu entorno
- `DISCORD_TOKEN`: tu token de bot de Discord.
- `SERVER_UPDATES_CHANNEL_ID`: el canal donde el bot envía anuncios.
- `DB_PATH`: ruta de la base de datos SQLite. En producción debe ser `/opt/discord-bot/data/bot.db`.
- `LOG_DIR`: ruta del directorio de logs. En producción debe ser `/opt/discord-bot/logs`.
- `TZ`: zona horaria para el scheduler; actualmente usa `Europe/Madrid`.

## Permisos y usuarios
- El servicio debe ejecutarse como `discord-bot`.
- El directorio `/opt/discord-bot/data` y el archivo `bot.db` deben ser escribibles por el grupo `discord-bot`.
- El directorio `/opt/discord-bot/logs` y `errors.log` deben ser escribibles por el grupo `discord-bot`.
- Si trabajas localmente con otro usuario, añádelo al grupo `discord-bot` para poder usar `/opt/discord-bot`.

## Despliegue recomendado
1. Copia el proyecto a `/opt/discord-bot/disc-mngmnt`.
2. Crea el virtualenv en `/opt/discord-bot/venv`:
   ```bash
   sudo python3 -m venv /opt/discord-bot/venv
   sudo /opt/discord-bot/venv/bin/pip install -r /opt/discord-bot/disc-mngmnt/requirements.txt
   ```
3. Ajusta permisos:
   ```bash
   sudo chown -R root:discord-bot /opt/discord-bot
   sudo chmod -R 770 /opt/discord-bot/data /opt/discord-bot/logs
   sudo chmod -R 750 /opt/discord-bot/disc-mngmnt
   ```
4. Configura el servicio systemd en `/etc/systemd/system/discord-bot.service`.
5. Habilita y arranca el servicio:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable discord-bot.service
   sudo systemctl start discord-bot.service
   ```

## Servicio systemd
El servicio creado es `discord-bot.service`. Su configuración principal es:

- `User=discord-bot`
- `Group=discord-bot`
- `WorkingDirectory=/opt/discord-bot/disc-mngmnt`
- `ExecStart=/opt/discord-bot/venv/bin/python /opt/discord-bot/disc-mngmnt/app/bot.py`
- `EnvironmentFile=/opt/discord-bot/disc-mngmnt/.env`

## Qué NO está implementado aún
- recordatorios (`reminders`)
- plan de raids con roles, threads y reacciones

## Notas finales
- Si el servicio arranca correctamente, el bot debe conectar y sincronizar comandos automáticamente.
- Para probar manualmente los jobs del scheduler, usa `/birthday_announce_upcoming` y `/birthday_announce_today`.
- Si cambias rutas, actualiza también `.env` y el servicio `systemd` si la ubicación del código cambia.