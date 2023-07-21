import discord
from discord import app_commands
import datetime
import traceback
import json
# The guild in which this slash command will be registered.
# It is recommended to have a test guild to separate from your "production" bot

with open('config.json', 'r') as f:
    config = json.load(f)
    TOKEN = config['TOKEN']

class MyClient(discord.Client):
    def __init__(self) -> None:
        # Just default intents and a `discord.Client` instance
        # We don't need a `commands.Bot` instance because we are not
        # creating text-based commands.
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        # We need an `discord.app_commands.CommandTree` instance
        # to register application commands (slash commands in this case)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        # Sync the application command with Discord.
        await self.tree.sync()


class CreatePA(discord.ui.Modal, title='PA'):
    mainname = discord.ui.TextInput(
        label='Main Name',
        placeholder='Leave empty if a main account',
        required=False
    )
    name = discord.ui.TextInput(
        label='Account Name',
        placeholder='Account name',
    
    )
    dateofenlistment = discord.ui.TextInput(
        label='Date of Enlistment',
        placeholder='DD/MM/YYYY'
    )

    prurl = discord.ui.TextInput(
        label='PR URL',
        placeholder='Enter PR URL or type TBA',
    )

    notes = discord.ui.TextInput(
        label='Notes',
        placeholder='Add Notes',
        max_length= 300
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild

        category_name = 'R&T'
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            await interaction.response.send_message(f"Category '{category_name}' not found.")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }

        role_names = ['admin','user']
        for role_name in role_names:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)
            else:
                await interaction.response.send_message(f"Role '{role_name}' not found. Skipping...")

        dateofenlistment = None
        try:
        # Attempt to parse the date string into a datetime object
            date = datetime.datetime.strptime(self.dateofenlistment.value, "%d/%m/%Y")
            dateofenlistment = date.strftime("%d/%m/%Y")
            # if(re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',self.prurl.value)):
            #     prurl = self.prurl.value
            # else:
            #     await interaction.response.send_message(f"Enter a valid PR URL") 
        except ValueError: 
            await interaction.response.send_message(f"{self.dateofenlistment.value} is not a valid date. Please use the format DD/MM/YYYY.")

        

        if dateofenlistment != None:
                
                if not self.mainname.value :
                    message = f"Date of Enlistment: {dateofenlistment}\nPR: {self.prurl.value}\nNotes: {self.notes.value} "
                    channel_name = f"main {self.name.value}"
                else :
                    message = f"Main Account: {self.mainname.value} \nDate of Enlistment: {dateofenlistment}\nPR: {self.prurl.value}\nNotes: {self.notes.value} "
                    channel_name = f"alt {self.name.value}"

                existing_channel = discord.utils.get(guild.channels, name=self.name.value)
                service_update = discord.utils.get(guild.channels, name="service-ribbon-update")
                if not existing_channel:
                    print(f'Creating a new channel: {self.name.value}')
                    new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)

                if message:
                    await new_channel.send(message)
                    await service_update.send(f'{self.name.value} - [{dateofenlistment}]')
                    await interaction.response.send_message(f'PA created for, {self.name.value}!', ephemeral=True)
        else :
            await interaction.response.send_message(f"Some data entered is wrong. Please try again") 
        # if not self.mainname.value :
        #     message = f"Date of Enlistment: {date}\nPR: {self.prurl.value}\nNotes: {self.notes.value} "
        #     channel_name = f"main {self.name.value}"
        # else :
        #     message = f"Main Account: {self.mainname.value} \nDate of Enlistment: {date}\nPR: {self.prurl.value}\nNotes: {self.notes.value} "
        #     channel_name = f"alt {self.name.value}"
            
        """ existing_channel = discord.utils.get(guild.channels, name=self.name.value)
        if not existing_channel:
            print(f'Creating a new channel: {self.name.value}')
            new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)

        if message:
            await new_channel.send(message)

            await interaction.response.send_message(f'PA created for, {self.name.value}!', ephemeral=True) """

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


client = MyClient()


@client.tree.command(name ="createpa" ,description="Create PA")
async def createpa(interaction: discord.Interaction):
    await interaction.response.send_modal(CreatePA())


client.run(TOKEN)