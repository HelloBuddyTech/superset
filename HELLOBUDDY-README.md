# HelloBuddy Superset

## Install and setup

### Install Superset

- Install Ubuntu Server 22
- Create a sudoable user:
```
sudo adduser hbsuperset
sudo adduser hbsuperset sudo
```
- Re-log as `hbsuperset`
```
sudo su hbsuperset
cd
```
- Create an SSH key:
```
ssh-keygen
cat .ssh/id_rsa.pub
# Prints something like ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCtRVISoiLue...
```
- Declare this key as a Deploy key:
  - Go to https://github.com/HelloBuddyTech/superset/settings/keys
  - Click "Add deploy key"
  - Fill the Title and copy/paste the value above as the Key.
  - Click "Add key"
- Get the code:
```
git clone git@github.com:HelloBuddyTech/superset.git
```
- Set `HELLOBUDDY_SUPERSET_SHARED_SECRET`. This value must be shared between Superset and HelloBuddy, so make sure to use the same value for the HelloBuddy app:
```
echo "HELLOBUDDY_SUPERSET_SHARED_SECRET=<the shared secret>" > superset/.superset_env
```
- Setup Docker:
```
cd superset/scripts
./setup_docker.sh
```
- Make sure `hbsuperset` can call Docker without `sudo`:
```
newgrp docker
docker run hello-world
```
- Setup Superset itself:
```
./setup_hellobuddy_supserset.sh
```

### Setup Superset

**Change the admin password!**

- Go to https://analytics.hellobuddy.tech/
- Login with admin/admin
- Go to Settings > Info
- Click "Reset my password"
- Choose a secured password

Configure the database connection:
- Go to https://app.planetscale.com/hellobuddy/hellobuddy/settings/passwords
- Click "New password"
- Type "analytics-hellobuddy-tech" as the name, select the "main" branch and "Read-only" the role, validate.
- Note the credentials.
- Go to https://analytics.hellobuddy.tech/, then Settings > Database Connections
- Click "+ Database"
- In the form:
  - Select MySQL
  - Port: 3306
  - Databse name, host, username and password are from the credentials provided by PlanetScape
  - Display name: "HelloBuddy - Production"
  - Enable SSL
- Click "Connect" twice.
- Click "Finish".

Create the data sets:
- Go to https://analytics.hellobuddy.tech/, then + > Data > Create dataset
- Select "HelloBuddy - Production" as the database and "hellobuddy" as the schema
- Select "Agent" as the table.
- Click "Create dataset and create chart"
- On the "Create a new chart" page, don't do anything.
- Repeat the procedure above the for following tables:
  - Agent (already done)
  - Answer
  - Customer
  - Mission
  - MissionTemplate
  - Notification
  - Question
  - QuestionCategory
  - Timing
  - User

## Update Superset

Perform and push the required changes in https://github.com/HelloBuddyTech/superset.

Then, connect to the hosting server:

```
cd superset
git pull
docker build -t hellobuddy-superset .
docker-compose -f docker-compose-non-dev.yml down
docker-compose -f docker-compose-non-dev.yml --env-file .superset_env up -d
```

## Create a Row Level Security (RLS) for an account

To configure the RLS for an account, you need:
- The account slug (eg. innoha)
- The account id (eg. cl8zmpd62003709xxxxxxxxxx)

- Go to https://analytics.hellobuddy.tech/, then Settings > Row Level Security
- Click "+"
- Fill the form:
  - Name: the account slug (eg. innoha)
  - Filter type: Regular
  - Tables: Select **all** tables (they have been listed as datasets)
  - Clause: `companyAccountId='<the company account id>'`
- Click "Save"

## OVH Virtual Machine

HelloBuddy Analytics is hosted on vps-9ac603ee.vps.ovh.net (54.36.181.187).

## Use AWS EC2


ssh -i aws-hellobuddy.pem ubuntu@3.252.27.109


## Nginx / Proxy

sudo apt install nginx certbot python3-certbot-nginx
sudo systemctl status nginx
sudo nano /etc/nginx/sites-available/default
sudo certbot --nginx -d supersetsandbox.hellobuddy.tech

## API

Maybe enable extra security API thanks to FAB_ADD_SECURITY_API, see https://github.com/apache/superset/issues/23300.

Edit superset/config.py and add:

```
FAB_ADD_SECURITY_API = True
```

Then update refresh the docs:

```
superset update-api-docs
```

A seen in superset/security/api.py, class is SecurityRestApi, permission name is grant_guest_token =>
{
  "permission": {
    "name": "can_grant_guest_token"
  },
  "view_menu": {
    "name": "SecurityRestApi"
  }
}

=> list_role_permissions

New docs available on http://<supsetset-instance>/swagger/v1

## How to set a role permission

Create a file named `my-role.json`.

Populate it with:

```
[
  {
    "name": "HelloBuddyApp",
    "permissions": [
      {
        "permission": {
            "name": "can_get"
        },
        "view_menu": {
            "name": "OpenApi"
        }
      },
      {
        "permission": {
            "name": "can_show"
        },
        "view_menu": {
            "name": "SwaggerView"
        }
      }, {
        "permission": {
            "name": "can_list_role_permissions"
        },
        "view_menu": {
            "name": "Role"
        }
      }
    ]
  }
]
```

How to find permission names? In the code (eg. `https://github.com/dpgaspar/Flask-AppBuilder/blob/090ddb4645992fb390da93906301c63b204db0df/flask_appbuilder/security/sqla/apis/role/api.py`), the `class_permission_name` is `Role`. And the permission name is set to `list_role_permissions` via `@permission_name`. So the JSON permission is:

```
{
  "permission": {
      "name": "can_list_role_permissions"
  },
  "view_menu": {
      "name": "Role"
  }
}
```

## From Scratch

https://superset.apache.org/docs/installation/installing-superset-from-scratch/

https://github.com/apache/superset/issues/19986#issuecomment-1143438882

## Recipes

### Add Security entry points

## Connect to the container

Run:

```
docker exec -it superset_app /bin/bash
```

# Enable Flask Security API

How to add the Flask beta Security API entry points:

```
docker exec -it superset_app /bin/bash
apt-get install -y nano
nano superset/config.py
  # Add a line:
  # FAB_ADD_SECURITY_API = True
superset init
mkdir -p docs/static/resources
superset update-api-docs
exit
# Back to host / out of Docker container
docker-compose -f docker-compose-non-dev.yml restart
```

## Support Google Sheets

From https://preset.io/blog/2020-06-01-connect-superset-google-sheets/:

```
cd superset
echo "gsheetsdb" >> ./docker/requirements-local.txt
docker-compose build --force-rm
docker-compose -f docker-compose-non-dev.yml up
```

## Embed / SSO

With AUTH_REMOTE_USER:
https://www.tetranyde.com/blog/embedding-superset
