[![Build Status](https://travis-ci.org/ccnmtl/uelc.svg?branch=master)](https://travis-ci.org/ccnmtl/uelc)

## docker-compose setup

[![Greenkeeper badge](https://badges.greenkeeper.io/ccnmtl/uelc.svg)](https://greenkeeper.io/)

Since uelc relies on windsock and a broker, the simplest way to have a
full local dev environment is to use Docker and
[docker-compose](https://docs.docker.com/compose/). The rest of this
assumes that you have those installed.

### build uelc image

This ensures that you have the most recent version of everything:

    $ make build

You will want to re-run this if you want to pick up on library updates
and such.

### set up initial database

The postgres database needs to be initialized.

    $ docker-compose run web migrate

This will probably take a few minutes since it will also take this
opportunity to download the other docker images that it needs
(postgres, windsock, windsock-broker) if they aren't already up to
date on your machine.

If the model changes in the future, re-running this step will also
update the existing database.

### run it

    $ docker-compose up

That should bring everything up. You'll see the database, windsock
server, and broker all starting up. The Django part will start up on
port 8000 as usual (with the same caveats about needing an HTTPS proxy
in front of it and hostname stuff set up for CAS access)

You can `C-c` at any point to shut things down (it might take a few
seconds).

From now on, for the most part, this is all you need to do.

For various maintenance-type tasks and debugging, you can also do, eg

    $ docker-compose run web shell

To get a django shell. Look at `docker-run.sh` for an idea of what
other actions are easily accessible.

### changing settings

You should be able to override django settings with a
`local_settings.py` as usual. If you need to run on a different port,
you'll need to change that in `docker-compose.yml`. If you are
changing it longer term, to avoid changing other devs' environments,
you will instead want to copy `docker-compose.yml`, make changes to
that and use `-f` on `docker-compose` commands to point at your
changed version.

You can change the logging level on windsock or the broker by adding
an environment variable like

    environment:
      - WINDSOCK_LOG_LEVEL=DEBUG

to its stanza (`BROKER_LOG_LEVEL` for the broker). Available log
levels are: `INFO` (default), `DEFAULT`, `WARN`, `ERROR`, and `FATAL`.
