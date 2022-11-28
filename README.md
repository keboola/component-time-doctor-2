
=============

Time Doctor 2 Extractor fetches data from TimeDoctor 2 API.


**Table of contents:**

[TOC]

Functionality notes
===================

Prerequisites
=============

To use this component you need user that is privileged to access data from used endpoints.


Supported endpoints
===================
- users
- tasks
- projects
- worklog
- edit-time
- timeuse

You can find more information about these endpoints in [TD2 API docs](https://api2.timedoctor.com/#/Activity/getActivityEditTime)

If you need more endpoints, please submit your request to
[ideas.keboola.com](https://ideas.keboola.com/)

Configuration
=============

## extractor configuration

 - Email (email) - [REQ] email for user whose credentials the data will be fetched
 - Password (#password) - [REQ] user's password
 - Company ID (company_id) - [OPT] Company ID - If not specified, component will fetch data for the first company
that companies endpoint will return.
 - From (from) - [OPT] Enter timestamp in `%Y-%m-%dT%H:%M:%S` format or a relative date of valid dateparser format. Defaults to now if empty.
 - To (to) - [OPT] Enter timestamp in `%Y-%m-%dT%H:%M:%S` format or a relative date of valid dateparser format. Defaults to now if empty.
 - users (_users) - [OPT] This endpoint is required to be processed for endpoints worklog, edit-time and timeuse
 - worklog (worklog) - [OPT] fetched data from worklog endpoint
 - edit-time (edit-time) - [OPT] fetches data from edit-time endpoint
 - timeuse (timeuse) - [OPT] fetches data from timeuse endpoint
 - projects (projects) - [OPT] fetches data from projects endpoint
 - tasks (tasks) - [OPT] fetches data from tasks endpoint
 - Incremental load (increment) - [OPT] If set to false, component will truncate data in existing Keboola tables.


Sample Configuration
=============
```json
{
    "parameters": {
        "endpoints": {
            "tasks": true,
            "_users": true,
            "timeuse": true,
            "worklog": true,
            "projects": true,
            "edit-time": true
        },
        "time-range": {
            "from": "14 days ago",
            "to": "now"
        },
        "authorization": {
            "email": "dominik@keboola.com",
            "#password": "gAAAxxXX8888XXX",
            "company_id": "YXjkhgEF18468461"
        }
    }
}
```

Output
======

List of tables, foreign keys, schema.

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in
the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/)