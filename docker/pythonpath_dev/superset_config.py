# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
from datetime import timedelta
from typing import Optional

from cachelib.file import FileSystemCache
from celery.schedules import crontab

logger = logging.getLogger()


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT")
DATABASE_DB = get_env_variable("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig(object):
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = ("superset.sql_lab",)
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "EMBEDDED_SUPERSET": True,
    'DRILL_TO_DETAIL': True,
    'DASHBOARD_RBAC': True
}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = "http://superset:8088/"
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

SQLLAB_CTAS_NO_LIMIT = True

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa

    logger.info(
        f"Loaded your Docker configuration at " f"[{superset_config_docker.__file__}]"
    )
except ImportError:
    logger.info("Using default Docker config...")


# Login via app.hellobuddy.tech


from flask_appbuilder.security.views import expose
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_appbuilder.security.manager import AUTH_REMOTE_USER
from flask import  redirect, request, flash
from flask_login import login_user

import hashlib
def compute_auth_token(email):
    secret = get_env_variable("HELLOBUDDY_SUPERSET_SHARED_SECRET")
    str = f'{secret}:{email}'
    return hashlib.sha256(str.encode("utf-8")).hexdigest()

# Create a custom view to authenticate the user
AuthRemoteUserView=BaseSecurityManager.authremoteuserview
class CustomAuthUserView(AuthRemoteUserView):
    @expose('/login/')
    def login(self):
        email = request.args.get('email')
        token = request.args.get('token')
        expected_token = compute_auth_token(email)
        next = request.args.get('next')
        sm = self.appbuilder.sm
        session = sm.get_session
        user = session.query(sm.user_model).filter_by(email=email).first()
        if (user is not None):
            if token == expected_token:
                login_user(user, remember=False, force=True)
                if (next is not None):
                    return redirect(next)
                else:
                    return redirect(self.appbuilder.get_url_for_index)
            else:
                #flash('Unable to auto login', 'warning')
                return super(CustomAuthUserView,self).login()
        else:
            #flash("User does not exist", 'warning')
            #return super(CustomAuthUserView,self).login()
            return redirect('/static/assets/logout.html')

# Create a custom Security manager that overrides the CustomAuthUserView
class CustomSecurityManager(SupersetSecurityManager):
    authremoteuserview = CustomAuthUserView

# Use our custom authenticator
CUSTOM_SECURITY_MANAGER = CustomSecurityManager

# User remote authentication
AUTH_TYPE = AUTH_REMOTE_USER

# Languages/i18n
BABEL_DEFAULT_LOCALE='fr'
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'fr': {'flag': 'fr', 'name': 'French'}
}

EXTRA_CATEGORICAL_COLOR_SCHEMES = [{
    "id": 'education',
    "description": '',
    "label": 'Education',
    "isDefault": False,
    "colors": [
        '#4B4BB7', '#FF2E63', '#7FE5C0', '#FFE600',
        '#242F6D', '#FF8DAE', '#00E536', '#FFB129',
        '#242F6D', '#FF0000', '#01CC88', '#FFD899'
    ]
}]
