### Prerequisites
=============

To use this component you need user that is privileged to access data from used endpoints.


### Supported endpoints
===================
- users
- tasks
- projects
- worklog
- edit-time
- timeuse

You can find more information about these endpoints in [TD2 API docs](https://api2.timedoctor.com/#/Activity/getActivityEditTime)

### Configuration
=============

#### Extractor configuration
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
