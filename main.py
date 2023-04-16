import os
import time

import requests
import schedule
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook


DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", None)
if DISCORD_WEBHOOK_URL is None:
    exit(1)

discord_webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)

def scrape() -> None:
    discord_embed = DiscordEmbed()

    r = requests.get("https://freethevbucks.com/timed-missions")
    soup = BeautifulSoup(r.content, features="lxml")

    for theater_container in soup.find_all("div", {"class": "col-xs-12"}):
        theater_name_element = theater_container.find("p", {"class": "jrfont"})

        theater_name = theater_name_element.text
        theater_name_element.decompose()
        
        mission_string_rewards = []

        for mission in theater_container.find_all("p"):
            mission_text = mission.text.split()

            mission_power_level = mission_text[0]
            mission_reward = " ".join(mission_text[1::])

            mission_string = f"`{mission_power_level:>3}`:zap:: {mission_reward}"
            mission_string_rewards.append(mission_string)

        discord_embed.add_embed_field(
            name=theater_name.title(),
            value="\n".join(mission_string_rewards),
            inline=False,
        )

    discord_webhook.add_embed(discord_embed)
    discord_webhook.execute()

    discord_webhook.remove_embeds()

if __name__ == "__main__":
    schedule.every().day.at("03:00", "Europe/Kiev").do(scrape)
    while True:
        schedule.run_pending()
        time.sleep(1)
