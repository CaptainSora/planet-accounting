import logging
from os import getenv

import disnake
from disnake.ext import commands, tasks
from dotenv import load_dotenv

import converters
import planets
import research


logging.basicConfig(level=logging.WARNING)
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("."),
    intents=intents
)


### Timers

class HSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scan.start()

    def cog_unload(self):
        self.scan.cancel()

    @tasks.loop(minutes=5.0)
    async def scan(self):
        await planets.check_planet_upgrade_status(self.channel)

    @scan.before_loop
    async def before_scan(self):
        print("HS Cog waiting...")
        await self.bot.wait_until_ready()
        print("HS Cog ready!")
        self.channel = self.bot.get_channel(1097421379005063268)
        if self.channel is None:
            print("Destination channel not found...")
            self.cog_unload()

bot.add_cog(HSCog(bot))


### Testing Commands

@bot.command()
async def test(ctx: commands.Context):
    await ctx.send("I'm alive!")


@test.error
async def info_error(ctx, error):
    await ctx.send("Beep boop that's an error mate")


### HS Slash Commands

@bot.slash_command()
async def hs(inter):
    # Check for any completed upgrades
    await planets.check_planet_upgrade_status(inter.channel)
    pass


@hs.sub_command(description=(
    "Starts an upgrade timer for an added planet."
))
async def upgrade_planet(
    inter,
    planet_name: str,
    duration: str = commands.Param(converter=converters.duration)
):
    await planets.upgrade_planet(inter, planet_name, duration)


@hs.sub_command(description=(
    "Shifts all upgrade times forwards. "
    "Useful to correct discrepancies due to TM usage."
))
async def shift_upgrade_times(
    inter,
    duration: str = commands.Param(converter=converters.duration)
):
    await planets.shift_upgrade_times(inter, duration)


@hs.sub_command(description=(
    "Adds or overwrites a planet on your list."
))
async def add_planet(
    inter,
    planet_name: str,
    level: commands.Range[1, 50],
    ptype: planets.PTYPE,
    tier: commands.Range[1, 4],
    disc: str = commands.Param(
        default = "", name="discriminator", choices=["a", "b"]
    )
):
    await planets.add_planet(inter, planet_name, level, ptype, tier, disc)


@hs.sub_command(description=(
    "Gives an overview of your planets."
))
async def list_planets(inter):
    await planets.list_planets(inter)


@hs.sub_command(description=(
    "Shows detailed upgrade info, including CC and suggested planet upgrade."
))
async def upgrade_details(inter):
    await planets.upgrade_details(inter)


@hs.sub_command(description=(
    "Computes how many arts you still need to research."
))
async def artifact_count(
    inter,
    art_level: commands.Range[1, 11],
    trade: str,
    mining: str,
    weapons: str,
    shields: str,
    support: str
):
    await research.artifact_count(
        inter, art_level, trade, mining, weapons, shields, support
    )


@hs.sub_command_group()
async def settings(inter):
    pass


@settings.sub_command(description=(
    "Set whether you want to be pinged when a planet upgrade completes."
))
async def ping_upgraded(inter, flag: bool):
    await planets.change_bool_settings(inter, "ping_when_upgraded", flag)


@settings.sub_command(description="Lists your settings.")
async def view(inter):
    await planets.view_settings(inter)


### Main

if __name__ == "__main__":
    load_dotenv()
    bot.run(getenv("API_ACCESS"))
