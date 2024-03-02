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
        label='👤  Main Name',
        placeholder='Leave empty if a main account',
        required=False
    )
    name = discord.ui.TextInput(
        label='👤  Account Name',
        placeholder='Account name',
    
    )
    dateofenlistment = discord.ui.TextInput(
        label='📅  Date of Enlistment',
        placeholder='DD/MM/YYYY'
    )

    prurl = discord.ui.TextInput(
        label='📎  PR URL',
        placeholder='Enter PR URL or type TBA',
    )

    notes = discord.ui.TextInput(
        label='📊  Evaluation',
        placeholder='Add Notes',
        max_length= 300
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild

        category_name = 'Personnel Administration'
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            await interaction.response.send_message(f"Category '{category_name}' not found.")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        #checking for server roles and assigning to the server
        role_names = ['R&T Command','Recruitment & Training', 'Non-Commissioned Officer', 'Chief Warrant Officer']
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

        except ValueError: 
            await interaction.response.send_message(f"{self.dateofenlistment.value} is not a valid date. Please use the format DD/MM/YYYY.")

        

        

        if dateofenlistment != None:
              #splitting main and alt accounts  
                service_update = discord.utils.get(guild.channels, name="service-ribbons-updates")
                if not self.mainname.value :
                    message1 = f"**👤 Recruit:** {self.name.value}\n**👥 Instructor's Name:** [Will be assigned by R&T Command]\n**📅 Date of Enlistment:**  {dateofenlistment}\n**📊 Evaluation:**  {self.notes.value} \n**📎 Personnel Record:**  {self.prurl.value} \n\n**📝 FIELD TRAINING PROGRAM (FTP) PROGRESS:**\n\n 👉 If you've completed any of the FTPs listed above, please add ✅️ check sign to check if the FTP has been completed or not by the instructor.\n\n👉 When completing a Field Training Program, we recommend focusing on one per day, rather than trying to complete all of them at once. This approach allows the trainee to properly absorb and understand the information presented in each FTP, which is essential for building a strong foundation of knowledge and skills.\n"
                    message3 = f"🛑 FTP 1: IC RULES, OOC RULES & RANK STRUCTURE"
                    message4 = f"🛑 FTP 2: TRAFFIC STOPS, ENGAGING IN FIREFIGHTS & RADIO COMMUNICATION"
                    message5 = f"🛑 FTP 3: ARRESTS, IC LAWS & IMPOUNDMENT"                   
                    #f"Date of Enlistment: {dateofenlistment}\nPR: {self.prurl.value}\nNotes: {self.notes.value} "
                    channel_name = f"main {self.name.value}"
                    await service_update.send(f'🏅  **{self.name.value}** - [{dateofenlistment}]')  
                else :
                    message1 = f"**👤 Recruit:** {self.name.value}\n**👥 Instructor's Name:** [Will be assigned by R&T Command]\n**📅 Date of Enlistment:**  {dateofenlistment}\n**📊 Evaluation:**  {self.notes.value} \n**📎 Main Account:** {self.mainname.value}\n**📎 Personnel Record:**  {self.prurl.value} \n\n**📝 FIELD TRAINING PROGRAM (FTP) PROGRESS:**\n\n 👉 If you've completed any of the FTPs listed above, please add ✅️ check sign to check if the FTP has been completed or not by the instructor.\n\n👉 When completing a Field Training Program, we recommend focusing on one per day, rather than trying to complete all of them at once. This approach allows the trainee to properly absorb and understand the information presented in each FTP, which is essential for building a strong foundation of knowledge and skills.\n"
                    message3 = f"🛑 FTP 1: IC RULES, OOC RULES & RANK STRUCTURE"
                    message4 = f"🛑 FTP 2: TRAFFIC STOPS, ENGAGING IN FIREFIGHTS & RADIO COMMUNICATION"
                    message5 = f"🛑 FTP 3: ARRESTS, IC LAWS & IMPOUNDMENT"
                    #message = f"Main Account: {self.mainname.value} \nDate of Enlistment: {dateofenlistment}\nPR: {self.prurl.value}\nNotes: {self.notes.value} "
                    channel_name = f"alt {self.name.value}"


################### NEED TO VALIDATE #######################
                existing_channel = discord.utils.get(guild.channels, name=self.name.value)
                
                if not existing_channel:
                    print(f'Creating a new channel: {self.name.value}')
                    new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)

                    await interaction.response.send_message(f'PA created for, {self.name.value}!', ephemeral=True)
                    await new_channel.send(message1)                                                     
                    await new_channel.send(message3)
                    await new_channel.send(message4)
                    await new_channel.send(message5)
                    
        else :
            await interaction.response.send_message(f"Some data entered is wrong. Please try again") 

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

   


client = MyClient()


@client.tree.command(name ="createpa" ,description="Create PA")
async def createpa(interaction: discord.Interaction):
    required_role_name = ['R&T Command','Recruitment & Training', 'Non-Commissioned Officer', 'Chief Warrant Officer','Commanding Officer']
    can_load = False
    for role in required_role_name:
        required_role = discord.utils.get(interaction.guild.roles, name=role)

        member = interaction.user

        if required_role in member.roles:
            can_load = True
            break            

    if can_load == True:
        await interaction.response.send_modal(CreatePA())
    else:
        await interaction.response.send_message(f"You do not have the required role to use this command.")

@client.tree.command(name ="editpa" ,description="Edit PA")
async def edit_message(ctx,channel_name: str, new_message: str):
    channel = discord.utils.get(ctx.guild.channels, name=channel_name)

    message_id = 1132163000715968613
    #message = await channel.fetch_message(message_id)
    message = await ctx.send("hello")
    #await asyncio.sleep(1)
    await message.edit(content="newcontent")

client.run(TOKEN)