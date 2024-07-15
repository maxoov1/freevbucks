import os
import sys

import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook


class AlertInformation:
    mission_power_level: int | str
    mission_reward_name: str

    def __init__(self, mission_power_level: int | str, mission_reward_name: str) -> None:
        self.mission_power_level = mission_power_level
        self.mission_reward_name = mission_reward_name


class TheaterInformation:
    name: str
    alerts_information: list[AlertInformation]

    def __init__(self, name: str) -> None:
        self.name = name
        self.alerts_information = []

    def add_reward(self, alert_information: AlertInformation):
        self.alerts_information.append(alert_information)


class ScrapeResults:
    theaters_information: list[TheaterInformation]

    def __init__(self) -> None:
        self.theaters_information = []

    def add_theater(self, theater_information: TheaterInformation):
        self.theaters_information.append(theater_information)


def scrape() -> ScrapeResults:
    r = requests.get("https://freethevbucks.com/timed-missions")
    soup = BeautifulSoup(r.content, features="lxml")

    scrape_results = ScrapeResults()

    for theater_container in soup.find_all("div", {"class": "col-xs-12"}):
        theater_name_element = theater_container.find("p", {"class": "jrfont"})
        theater_name = theater_name_element.text

        # remove theater element from the tree
        theater_name_element.decompose()

        theater_information = TheaterInformation(name=theater_name)

        for mission in theater_container.find_all("p"):
            mission_text = mission.text.split()

            mission_power_level = mission_text[0]
            mission_reward = " ".join(mission_text[1::])

            alert_information = AlertInformation(
                mission_power_level=mission_power_level, mission_reward_name=mission_reward)
            theater_information.add_reward(alert_information=alert_information)

        scrape_results.add_theater(theater_information=theater_information)

    return scrape_results


class DiscordWebhookAlert:
    def __init__(self, webhook_url: str):
        self.webhook = DiscordWebhook(url=webhook_url)

    def execute(self, scrape_results: ScrapeResults) -> None:
        embed = DiscordEmbed()

        for theater in scrape_results.theaters_information:
            theater_rewards_string = \
                "\n".join(f"`{reward.mission_power_level:>3}`:zap:: {reward.mission_reward_name}"
                    for reward in theater.alerts_information)

            embed.add_embed_field(
                name=theater.name.title(), value=theater_rewards_string, inline=False,
            )

        self.webhook.add_embed(embed)
        self.webhook.execute()

        self.webhook.remove_embeds()


def main() -> None:
    DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", None)
    if DISCORD_WEBHOOK_URL is None:
        sys.exit("DISCORD_WEBHOOK_URL environment variable is not set")

    discord_webhook_alert = DiscordWebhookAlert(webhook_url=DISCORD_WEBHOOK_URL)
    scrape_results = scrape()

    discord_webhook_alert.execute(scrape_results)


if __name__ == "__main__":
    main()
