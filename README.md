# CF Discord Notification Bot

<p align="center">
  <img src="resources/CFN Icon.png" alt="CFN Icon" height="256" width="256"/>
</p>

[![Codacy Badge][codacy_badge]][codacy_link]
[![License][license-image]][license-url]
[![GitHub Release][github_release_badge]][github_release_link]
[![Donate][pateron_badge]][pateron_link]
[![Top.gg][top_gg_badge]][top_gg_link]
[![Support Discord][discord_badge]][discord_inv]

A discord bot that allows you to set reminders on your server for upcoming [codeforces][codeforces] rounds.

## Features

To get the full list of commands type `;help` after adding the bot to the server.

### Upcoming Contests

Use `;upcoming` to get the upcoming contest on codeforces.

![Upcoming_Example](resources/readme/Upcoming_Example.jpg)

### Contest Notifications

Use `;rfn @ROLE_TO_NOTIFIY` to register a channel for notifications.

![Register Example](resources/readme/Register_Example.jpg)

![Notification Example](resources/readme/Notification_Example.jpg)

## Running the code

You can run the code using any of the following methods.

### Venv

Install the required python modules (perferably in a virtual env) to be able to run the bot.

``` bash
Python -m venv venv
venv\Scripts\activate.bat
Pip install -r requirements.txt
```

Then copy the `.env.example` file and rename it to `.env` and fill in the appropriate values.

Run the bot using the followingL

```bash
python -m CFDiscordNotificationBot
```

### Docker

First make sure u have docker installed. Build the image from the dockerfile then run an container using the following commands.

```bash
docker build -t cfnbot:latest .
docker run --rm -d -v CFNdata:/usr/src/app/Data/ --name CFN cfnbot:latest
```

To stop the container:

```bash
docker stop CFN
```

### Docker-compose

First make sure u have docker compose installed. Run the following command to start the container.

```bash
docker-compose up
```

Use ``--build`` if there has been a change to the Dockerfile.

```bash
docker-compose up --build
```

To stop the container:

```bash
docker-compose down
```

If you to use the same volume as docker change the volume part of docker-compose.yml to:

```yaml
volumes:
    CFNdata:
        external: true
```

## Built With

* [VS Code](https://code.visualstudio.com/) - Editor
* [PyCharm](https://www.jetbrains.com/pycharm/) - Editor
* [Photopea](https://www.photopea.com/) - Image editor

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

[SemVer](http://semver.org/) was used for versioning. For the versions available, see the [tags on this repository](https://github.com/TheDigitalPhoenixX/CFDiscordNotificationBot/tags). For the Changelog see the [CHANGELOG](CHANGELOG.MD/) file.

## Authors

* **Mohamed Said** - [TheDigitalPhoenixX](https://github.com/TheDigitalPhoenixX)
* **Sameh Amnoun** - [SamehAmnoun](https://github.com/SamehAmnoun)

See also the list of [contributors](CONTRIBUTORS.md) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [README.md Template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)

[license-image]: https://img.shields.io/badge/License-MIT-brightgreen.svg
[license-url]: https://opensource.org/licenses/MIT

[codeforces]: https://codeforces.com/

[github_release_badge]: https://img.shields.io/github/v/release/TheDigitalPhoenixX/CFDiscordNotificationBot.svg?style=flat
[github_release_link]: https://github.com/TheDigitalPhoenixX/CFDiscordNotificationBot/releases

[top_gg_badge]: https://img.shields.io/badge/Add%20to%20your%20server-Top.gg-7289da
[top_gg_link]: https://top.gg/bot/702589426487918733

[codacy_badge]: https://api.codacy.com/project/badge/Grade/66e0a4c4474c41bf86a9463b805b94a3
[codacy_link]: https://www.codacy.com/manual/OrganizationX/CFDiscordNotificationBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=TheDigitalPhoenixX/CFDiscordNotificationBot&amp;utm_campaign=Badge_Grade

[pateron_badge]: https://img.shields.io/badge/Patreon-support-f96854.svg?style=flat
[pateron_link]: https://www.patreon.com/user?u=35000497

[discord_badge]: https://discordapp.com/api/guilds/707807869650599947/widget.png
[discord_inv]: https://discord.gg/qVxjDDd
