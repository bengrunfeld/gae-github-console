# The WebFilings Github Console

The WebFilings Github Console allows the members of the organization who do not possess admin rights to create private repositories, add and remove teams from those repositories, and add and remove users from those teams.

The console also provides logs of what actions were performed by which user. These logs can be filtered by date range. A regular digest of logs can be sent to a specific email as a CRON job. The filtered logs can be manually emailed to a specific email address.

## Activate the app

Before uploading the app to GAE, open `app.yaml` and enter the exact name of the Github organization in the space to the right of the `ORG` environment variable.

To set up the CRON job that sends a daily email to a specific address, enter the address to the right of the `ADMIN_EMAIL` environment variable. 

Save and close `app.yaml`.
 
To activate the app once you've uploaded it to GAE, a user who belongs to the `Owners` team in the organization needs to log in via the console. They will be directed to the Github auth page, where they will need to provide their credentials. Once they have been authorized, their access token will be stored by the app in Google's Datastore and used by the app to perform actions (e.g. create new private repo) on their behalf.

Any user belonging to the organization (i.e. not an admin) can then log in and access all the features of the app.

## Using the app

#### View all private repositories

Once a user has logged in, they will see an interface with a list of all the private repositories belonging to the organization.

#### Create private repos

Above the main listing window, there is a `Create Private Repo` button. Pressing it will bring up a modal allowing the user to specify the name of the private repository they'd like to create and a short description of the repository.

#### Logs

Underneath the `Create Private Repo` button, there is a `Display Logs` button. Clicking it will bring up a modal that shows the most recent logs. There are options that allow the user to filter the date range of the logs. An option exists which allows the user to send all logs, or the filtered logs to an email address.

A regular digest of all logs is sent out automagically to the specified recipient (setup instructions above).

#### Editing access to a private repo

Next to the listing of each private repo, there is an `Edit Access` button. Clicking on it will bring up a modal that allows the user to add a team belonging to the organization to the repo. Once added, the user can then change the access permission of that team. Not that this changes the access of the team to all other repositories that it is connected to.

Access levels can be either `Push` or `Pull`.

#### Adding and removing organization members from a team

At the top of the `Edit Access` modal, there are 2 tabs – `Teams` and `Team Members`. 

If the user clicks on the `Team Members` tab, they will see a tab where organization members can be added or removed from a team. 

The top selection box allows the user to select the team that they'd like to edit. The second selection box contains the existing members of that team. Next to each team member name is a `Remove` button. Clicking it will remove that member from the team.

The third selection box contains the names of all members in the organization who are not members of the team. The user can select multiple members by holding down the `Command` or `Shift` keys and making a selection. Clicking `Add` at the bottom of the modal will add those members to the team.
