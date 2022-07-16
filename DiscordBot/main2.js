//Import library
const {Client, Intents} = require('discord.js');
const myToken = require('./config.json');

//Client creation
const client = new Client({ intents: [Intents.FLAGS.GUILDS] }, {partials: ["MESSAGE", "CHANNEL", "REACTION"]});
const prefix = '-';

//When ready do this
client.once('ready', () => {
    console.log('WipeEnjoyer Ready!');
})

//Command execution
client.on('message', message =>{
    if(!message.content.startsWith(prefix) || message.author.bot) return ;

    const args =message.content.slice(prefix.length).split(/ +/);
    const command = args.shift().toLowerCase();

    //Possible commands
    if (command === 'ping'){
        message.channel.send('pong');
    } else if (command === 'reactionRole'){
        client.commands.get('reactionRole').execute(message, args, Client, client);
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
client.login(myToken.token);