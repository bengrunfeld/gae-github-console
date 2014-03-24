# Github Console

The Github console allows for the creation of private repositories within
an organization.

It also displays existing private repositories.

For any priate repository, a user with administrative priveledges can 
add/remove other users within the same organization as collaborators, and may 
also add/remove teams as having push/pull access to the repo.

The main aim of the console is to place strict controls around a person elected
to be an admin in an organization, while still allowing that admin user to 
create, edit and delete private repositories at will.

Twitter Bootstrap has been used for the frontend so the app is mobile friendly.

For the backend, Python has been used on top of the Google App Engine
infrastructure.

## Set up the app for your organization

To customize the app to your needs, edit app.yaml and replace the following
values of the following environment variables with your own:   

    CLIENT_ID
    CLIENT_SECRET
    ORG

