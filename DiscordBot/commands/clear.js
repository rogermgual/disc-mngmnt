module.exports = {
    name: 'clear',
    description: 'Clear all messages!',
    async execute(message, args, Discord){
        const newEmbed = new Discord.MessageEmbed()
        await message.channel.messages.fetch({limit: args[0]}.then( messages => messages.channel.bulkDelete(messages) ));
    }
}