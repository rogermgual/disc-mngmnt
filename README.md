# Discord Management python bot
Python slash commands

## Functionalities
### At this moment
- Say hello to the person who /hello
- Plays ping pong with who /ping

### To implement
- Birthday
    - Register one user birthday in DD/MM format
    - The day of the user's birthday, the bot sends a predefined message tagging @everyone, on a predefined channel
    - Each monday, if there is a birthday approaching on that week, will send a predefined message on a predefined channel with the people who's birthdaying
    - Each user can only modify it's own birthday
    - Each user can only have a single birthay

- Reminders
    - Registers an event/message to be reminded
    - Choose if punctual or recursive
        - Both will need a DD/MM/YYYY HH:MM format date for the first remember
        - If recursive, will need to specify frequency
            - Daily: everyday
                - Be careful with the spam
            - Weekly: Choose which day(s) of the week
            - Monthly: choose a number (1-31)
                - If selects 31 in a 28/30-day-month, the last day will be registered (28 or 30)
    - The message will be send on the channel at the time previously configured
    - Each user can only edit or delete its own messages

- Raid plan
    - Register a raid event
    - The bot will send a message in an specific channel with the raid event in format <raid-event-name>-<dd-mm-yyy>
    - The bot will create a role with the name of the event (in the previous mentioned format)
    - The bot will open a thread in that specific message
    - The bot will only accept emoji reactions :tank: :healer: :dps-melee: :dps-caster: :dps-ranged:
        - Each time someone reacts with one of this emojis, the bot will grant the event role to that user
            - The bot only will accept a maximum number of people per each reaction:
                - 2 for tank
                - 2 for heal
                - 2 for melee
                - 1 for caster
                - 1 for ranged
            - If some one reacts with another icon, the bot will ignore it
            - Each time someone reacts to the icon, the bot will tag that user with a message and the icon selected inside the thread
            - If some one reacts to a full role, the bot will create a new rol, with the same name of the event but adding a "-backup"
                - The user will be noticed as well in the thread with the same icon, but noticing it will be a backup
    - 1 hour before the event start, the bot will tag the role in the thread in order to warn people
    - The user that create the event will be responsible of the post-event process
        - There will be a function to "close" the event that will
            - Say thanks to @role 
            - Close and block the thread
            - Delete the roles created
        - If it is not done manually, the bot will do it automatically 24h later of the start of the event
