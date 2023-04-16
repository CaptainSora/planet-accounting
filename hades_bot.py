import logging
from os import getenv

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
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


@bot.slash_command(
    name="Upgrade Planet",
    description="Marks a planet as upgrading"
)
async def upgrade_planet(
    inter,
    planet_name: str,
    level: commands.Range[1, 50]
):
    await inter.response.send_message(
        f"Upgrading planet {planet_name} to level {level}"
    )



if __name__ == "__main__":
    load_dotenv()
    bot.run(getenv("API_ACCESS"))
