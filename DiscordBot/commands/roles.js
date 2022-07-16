const { Emoji } = require("discord.js");

module.exports = {
    name: 'reactionRole',
    description: 'Set up a role based on the reaction',
    async execute(msg, args, Discord, client)  {
        //Selección del canal
        const channel = '997685959061688421';

        //DEFINICIONES
        //Discord General Roles
        const memeberRole = message.guild.roles.cache.find(role => role.name === "Miembro")
        const ffxivRole = message.guild.roles.cache.find(role => role.name === "FF X|V")
        const lolRole = message.guild.roles.cache.find(role => role.name === "LoL")

        //FFXIV Roles
        const tankXIV = message.guild.roles.cache.find(role => role.name === "tank")
        const healerXIV = message.guild.roles.cache.find(role => role.name === "healer")
        const dpsMXIV = message.guild.roles.cache.find(role => role.name === "dps-melee")
        const dpsCXIV = message.guild.roles.cache.find(role => role.name === "dps-caster")
        const dpsRXIV = message.guild.roles.cache.find(role => role.name === "dps-ranged")

        //Emojis to be related
        const memeberIcon = ':bust_in_silhouette:';
        const ffxivRoleIcon = ':video_game:';
        const lolRoleIcon = ':wheelchair:';
        const tankIcon = ':shield:';
        const healerIcon = ':hospital:';
        const meleeIcon = ':crossed_swords:';
        const casterIcon = ':mage:';
        const rangedIcon = ':bow_and_arrow:';

        
        //Mensaje
        let embed = new Discord.MessageEmebed()
        .setColor('')
        .setTitle('SELECCIONA TUS ROLES \n')
        .setDescription('Como  mínimo debéis tener el rol de "Miembro" para poder ver los canales comunes: \n \n'
            + `${memeberIcon} para ser MIEMBRO\n`
            + `${ffxivRoleIcon} para ver contenido relacionado con FFXIV\n`
            + `${lolRoleIcon} para ver contenido relacionado con LOL\n`
        );
        
        //Reacciones al emoji
        let messageEmebed = await message.channel.send();
        messageEmebed.react(memeberIcon);
        messageEmebed.react(ffxivRoleIcon);
        messageEmebed.react(lolRoleIcon);

        client.on('messageReactionAdd', async(reaction, user) => {
            if (reaction.message.partial) await reaction.message.fetch();
            if (reaction.partial) await reaction.fetch();

            //Nos aseguramos de quién puede usar el bot
            if(user.bot) return;
            if(!reaction.message.guild) return;

            //Nos aseguramos de contestar en el mismo chat
            if (reaction.message.channel.id == channel) {
                if(reaction.emoji.name === memeberIcon){
                    await reaction.message.guild.memebers.cache.get(user.id).roles.add(memeberRole);
                }
                if(reaction.emoji.name === memeberIcon){
                    await reaction.message.guild.memebers.cache.get(user.id).roles.add(ffxivRole);
                }
                if(reaction.emoji.name === memeberIcon){
                    await reaction.message.guild.memebers.cache.get(user.id).roles.add(lolRole);
                } else {
                    return;
                }
            }

        });

        client.on('messageReactionRemove', async(reaction, user) => {
            if (reaction.message.partial) await reaction.message.fetch();
            if (reaction.partial) await reaction.fetch();

            //Nos aseguramos de quién puede usar el bot
            if(user.bot) return;
            if(!reaction.message.guild) return;

            //Nos aseguramos de contestar en el mismo chat
            if (reaction.message.channel.id == channel) {
                if(reaction.emoji.name === memeberIcon){
                    await reaction.message.guild.memebers.cache.get(user.id).roles.remove(memeberRole);
                }
                if(reaction.emoji.name === memeberIcon){
                    await reaction.message.guild.memebers.cache.get(user.id).roles.remove(ffxivRole);
                }
                if(reaction.emoji.name === memeberIcon){
                    await reaction.message.guild.memebers.cache.get(user.id).roles.remove(lolRole);
                } else {
                    return;
                }
            }

        });
    }
}