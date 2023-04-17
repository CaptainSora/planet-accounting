import logging
from os import getenv

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

import converters
import planets


logging.basicConfig(level=logging.WARNING)
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("."),
    intents=intents
)


@bot.command()
async def test(ctx: commands.Context):
    await ctx.send("I'm alive!")


@test.error
async def info_error(ctx, error):
    await ctx.send("Beep boop that's an error mate")


@bot.slash_command()
async def hs(inter):
    # Check for any completed upgrades
    await planets.check_planet_upgrade_status(inter.channel)
    pass


@hs.sub_command(description="Marks a planet as upgrading.")
async def upgrade_planet(
    inter,
    planet_name: str,
    duration: str = commands.Param(converter=converters.duration)
):
    await planets.upgrade_planet(inter, planet_name, duration)


@hs.sub_command(description="Adds a planet to your list.")
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


@hs.sub_command(description="Lists your planets.")
async def list_planets(inter):
    await planets.list_planets(inter)


@hs.sub_command(description="Lists detailed upgrade info.")
async def upgrade_details(inter):
    await planets.upgrade_details(inter)


@hs.sub_command_group()
async def settings(inter):
    pass


@settings.sub_command(
    description="Whether you want to be pinged when a planet upgrade completes."
)
async def ping_upgraded(inter, flag: bool):
    await planets.change_bool_settings(inter, "ping_when_upgraded", flag)


@settings.sub_command(description="Lists your settings.")
async def view(inter):
    await planets.view_settings(inter)


if __name__ == "__main__":
    load_dotenv()
    bot.run(getenv("API_ACCESS"))
