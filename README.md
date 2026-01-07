# NextGen

This repo contains the components of the nextgen infrastructure. This is a monorepo, so all frontend and backend code can remain in sync.

## Setup

To setup your devcubby with the necessary settings and tools, just run `./scripts/setup.sh`.

## Developing

The api is powered by python, which runs inside a docker container. Run `docker-compose up -d` to start your docker containers.

Next, make sure your yarn dependencies are up to date by running `yarn` and then compile the app and watch for changes using `yarn dev`.

**Note: please use yarn, not npm**

This app uses yarn workspaces, so yarn installation and commands should be run from the root of the project. But when installing new dependencies (i.e. `yarn add somepackage`), these should be run from the directory they correspond to.

### Domains

There are 3 subdomains associated to this repo. They are all automatically configured by the setup script.

- api.yourcubbydomain.sknv.cubby.zone: The django api
- app.yourcubbydomain.sknv.cubby.zone: The react app
- dashboard.yourcubbydomain.sknv.cubby.zone: The celery dashboard

### Directory Structure

All application code is organized into "apps" in the `apps/` directory.

- `apps/frontend/` contains the React app
- `apps/api/` contains the Django API and celery tasks

Any infrastructure-related files, such as specific docker files or other environment config files are in the `infrastructure` directory.

Helper scripts are in the `scripts` directory. In most cases, these should be targeted at development environments. Scripts related to higher environments (prod, test, etc) should be part of environment-specific configurations in either the `infrastructure` directory or the elasticbeanstalk config for each app.

## Scheduled Tasks

To add a new scheduled task, add it to the `CELERY_BEAT_SCHEDULE` in `apps/api/core/settings.py` and ensure it references a valid task.
