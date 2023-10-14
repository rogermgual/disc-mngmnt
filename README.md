

## How to create new images with your own token
Build the docker image with the specific Discord Token
```docker build -t wipeingway-bot -e DISCORD_TOKEN=<discord token here> .``

Run the container image
```docker run -it --rm wipeingway-bot```