//Import library
const {Client, Intents} = require('discord.js');

//Client creation
const client = new Client({ intents: [Intents.FLAGS.GUILDS] }, {partials: ["MESSAGE", "CHANNEL", "REACTION"]});
const prefix = '-';

//When ready do this
client.once('ready', () => {
    console.log('WipeEnjoyer Ready!');
})

//Command execution
client.on('message', message =>{
    if(!message.content.startswith(prefix) ||message.author.bot) return ;

    const args =message.content.slice(prefix.length).split(/ + /);
    const command = args.shift().toLowerCase();

    //Possible commands
    if (command === 'ping'){
        message.channel.send('pong');
        print("PONG")
    } else if (command === 'reactionRole'){
        client.commands.get('reactionRole').execute(message, args, Discord, client);
    }
    else{
        message.channel.send('Este comando no está disponible (de momento)');
    }
    /*
    if (command === ''){

    }
    */
});

//Bot Token
client.login('OTk3NzA5OTE5NTA1NjMzMzUw.G_hZCn.5J7QtjZ18y21OQU0OS7wyfrHnrXnzvXnzWiToM');