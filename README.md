# Trellbot

## Project Summary

This project was started with a co-contributor in summer of 2020, and ended in fall of 2020.
I lead the project development, and managed the Trello Board for each sprint during the project.

The purpose of the project was to create a Discord integration with Trello, using the Trello and Discord APIs.
Further development would've been focused on user privacy, and implementation of redis.

-----

When setting up the bot you will need a ".env" file containing the following line:

COMMAND_START="{YOURCOMMANDSTART}"

DISCORD-TOKEN={REPLACE WITH TOKEN}

ADMIN_GUILD_ID={YOUR ADMIN GUILD ID}

-----

Trellbot is built upon the following Python3 Libraries:

Dotenv ->
pip install -U python-dotenv

Discord.py ->
pip install -U discord.py

Py-Trello ->
pip install py-trello

Safer ->
pip install safer

-----

The Licenses For Each Are:

Dotenv     - BSD-3 License

Discord.py - MIT License

Py-Trello  - BSD-3 License

Safer      - MIT License
