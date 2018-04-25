======================
Slackcast OAuth Helper
======================

AWS Lambda function to get Slack token using OAuth2.

Free software: MIT license

Installation
------------

Use with Zappa.

Create a `zappa_settings.yaml` file::

    dev:
      app_function: slackcast_oauth.app
      aws_region: us-east-1
      profile_name: default
      runtime: python3.6
      project_name: slackcast_oauth
      environment_variables:
        SLACKCAST_CLIENT_ID: "<SLACK_CLIENT_ID>"
        SLACKCAST_CLIENT_SECRET: "<SLACK_CLIENT_SECRET"

