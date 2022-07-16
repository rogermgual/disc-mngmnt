module.exports = {
    name: 'command',
    description: 'Embeds!',
    execute(message, args, Discord){
        const newEmbed = new Discord.MessageEmbed()
        .setTitle('Test')
        .setDescription('This is a test message')
    }
}