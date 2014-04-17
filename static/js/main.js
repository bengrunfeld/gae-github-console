$(function(){

    $('.edit-repo').click(get_data);
    $('.display-logs').click(display_logs);
    $('.add-date-filter').click(add_date_filter);
    $('.reset-date-filter').click(reset_date_filter);
    $('.email-logs').click(email_logs);

    // Bind events related to Edit Access
    function bind_events() {
        $('.add-team').click(add_team);
        $('.remove-team').click(remove_team);
        $('.make-admin').click(edit_team);
        $('.make-push').click(edit_team);
        $('.make-pull').click(edit_team);
        $('.list-all-teams').change(change_team);
        $('.add-team-members').click(add_team_members);
    }

    //Pull all relevant data to populate the modal
    function get_data(repo_name){
        
        // Set the repo name. If it's not passed as a param, 
        // grab the repo name of the button that was clicked on
        var repo = typeof(repo_name) !== 'string' ? $(this).attr('value') : repo_name;

        // Place repo name as modal heading
        $('.panel-repo-name').html(repo);

        // Get user and team data for the repo
        $.ajax({
            type: "POST",
            url: "/get-data",
            data: { "repo" : repo },
            success: function(data) {
                if(data) {
                    data = JSON.parse(data);
                    
                    $('.members').remove();
                    $('.collaborators').remove();
                    $('.teams').remove();
                    $('.team_collaborators').remove();
                    $('.all-teams').remove();   

                    // Print out all the teams in the org, as long as they are not assigned to a repo
                    if(data.teams) {
                        for(var key in data.teams){
                            $('.list-teams').append('<li class="list-group-item teams"><span class="team">' + key + '<span class="permission"> (' + data.teams[key][1] + ')</span>' + '</span><button type="button" class="btn btn-success btn-sm team-btn add-team pull-right" id="' + data.teams[key][0] + '" name="' + key + '">Add Team</button></li>');
                        }
                    }

                    // Print out repo teams and the 'edit access' buttons
                    if(data.team_collaborators) {
                        for(var key in data.team_collaborators){
                            permission = data.team_collaborators[key][1]
                            var content = '<li class="list-group-item team_collaborators"><span class="team_collaborator" name="' + key + '">' + key + '<span class="permission"> (' + data.team_collaborators[key][1] + ')</span>' + '</span>';
                            content += '<button type="button" id="' + data.team_collaborators[key][0] + '" class="close remove-team" name="' + key + '" aria-hidden="true">&times;</button>';

                            switch(permission) {
                                case "admin":
                                    content += '<button type="button" id="' + data.team_collaborators[key][0] + '" class="btn btn-danger btn-sm team-btn make-pull pull-right" name="' + key + '" value="pull">Make Pull</button>';
                                    content += '<button type="button" id="' + data.team_collaborators[key][0] + '" class="btn btn-danger btn-sm team-btn make-push pull-right" name="' + key + '" value="push">Make Push</button>';                                    
                                    break;
                                case "push":
                                    content += '<button type="button" id="' + data.team_collaborators[key][0] + '" class="btn btn-danger btn-sm team-btn make-pull pull-right" name="' + key + '" value="pull">Make Pull</button>';
                                    break;
                                case "pull":
                                    content += '<button type="button" id="' + data.team_collaborators[key][0] + '" class="btn btn-danger btn-sm team-btn make-push pull-right" name="' + key + '" value="push">Make Push</button>';
                                    break;
                                default:
                            }
                            content += '</li>';
                            $('.list-team-collaborators').append(content);
                        }
                    }

                    // List all teams in the Team Members select box
                    if(data.all_teams) {
                        for(var key in data.all_teams){
                            $('.list-all-teams').append('<option class="all-teams" value="' + data.all_teams[key][0] + '">' + key + '</option>');
                        }
                    }

                    // Bind events once everything has loaded
                    bind_events();
                }
            }
        });
    }

    // Add a team to a repo
    function add_team() {

        // Get the repo name
        var repo = $('.panel-repo-name').html();

        // Get the team id
        var team_id = $(this).attr('id');

        // Get the team name
        var team_name = $(this).attr('name');

        // Give the team Push Access
        $.ajax({
            type: "POST",
            url: "/add-team",
            data: { "repo": repo, "team_id": team_id, "team_name": team_name },
            success: function(data) {
                var repo_name = repo;
                get_data(repo_name);
            }
        });
    }

    // Remove a team from a repo
    function remove_team() {

        // Get the repo name
        var repo = $('.panel-repo-name').html();

        // Get the team id
        var team_id = $(this).attr('id');

        // Get the team name
        var team_name = $(this).attr('name');

        // Give the team Push Access
        $.ajax({
            type: "POST",
            url: "/remove-team",
            data: { "repo": repo, "team_id": team_id, "team_name": team_name },
            success: function(data) {
                var repo_name = repo;
                get_data(repo_name);
            }
        });
    }

    // Edit team access
    function edit_team() {

        // Get the repo name
        var repo = $('.panel-repo-name').html();
        
        // Get the team id
        var team_id = $(this).attr('id');

        // Get the team name
        var team_name = $(this).attr('name');

        // Get the edit action
        var edit_type = $(this).attr('value');        

        // Send to main.py
        $.ajax({
            type: "POST",
            url: "/edit-team",
            data: { "team_id" : team_id, "team_name": team_name, "edit_type" : edit_type },
            success: function(data) {
                var repo_name = repo;
                get_data(repo_name);
            }
        });
    }

    // Print all the members of a team when a user chooses a different team to edit in the Team Members tab
    function change_team() {

        // Get the repo name
        var repo = $('.panel-repo-name').text();

        // Send to main.py
        $.ajax({
            type: 'POST',
            url: '/change-team',
            data: { "team_id" : $('.list-all-teams').find('option:selected').attr('value') },
            success: function(data) {
                
                // Parse the JSON
                var members = JSON.parse(data);
                var team_members = members['team_members'];
                var all_members = members['all_members'];

                // Remove any previous results
                $('.team-member').remove();

                // List all team members of the selected team
                if(team_members) {
                    for(var i=0; i<team_members.length; i++){
                        $('.list-team-members').append('<li class="list-group-item team-member">' + team_members[i] + '<button class="btn btn-danger btn-sm team-btn make-pull pull-right remove-member" value="' + team_members[i] + '">Remove</button></li>');
                    }
                }

                // Set an event handler for the Remove buttons
                $('.remove-member').click(remove_member);

                // Remove any previous results
                $('.members').remove();

                //List all Members in the Org
                if(all_members) {
                    for(var i=0; i<all_members.length; i++){
                        if(jQuery.inArray(all_members[i], team_members) == -1) {
                            $('.list-members').append('<option class="members" value="' + all_members[i] + '">' + all_members[i] + '</option>');
                        }
                    }
                }

            }
        });
    }

    // Add a member of the org to a team
    function add_team_members() {

        // Get the repo name
        var repo = $('.panel-repo-name').text();
        
        // Get the team id
        var team_id = $('.list-all-teams').find('option:selected').attr('value');

        // Get the usernames
        var members = [];

        // Push members into a list of usernames
        $(".list-members option:selected").map(function(){ members.push(this.value); });

        // Prepare the array to be sent through the AJAX request
        var users = JSON.stringify(members);

        // Send to main.py
        $.ajax({
            type: "POST",
            url: "/add-team-members",
            data: { "team_id" : team_id, "users": users},
            success: function(data) {
                change_team();
            }
        });
    }

    // Remove a member of the org from a team
    function remove_member() {

        // Get the repo name
        var repo = $('.panel-repo-name').text();

        // Get the team id
        var team_id = $('.list-all-teams').find('option:selected').attr('value');

        // Get the user
        var user = $(this).attr('value');

        // Send to main.py
        $.ajax({
            type: "POST",
            url: "/remove-team-member",
            data: { "team_id" : team_id, "user": user},
            success: function(data) {
                change_team();
            }
        });
    }

    // Display most recent logs
    function display_logs(event, from_datetime, to_datetime) {

        // If params are not set, set them as empty. `false` does not translate well into python
        var from_date = typeof(from_datetime) == ('undefined' || false) ? false : JSON.stringify(from_datetime);
        var to_date = typeof(to_datetime) == ('undefined' || false) ? false : JSON.stringify(to_datetime);

        // Activate the log script in main.py
        $.ajax({
            type: "POST",
            url: "/display-logs",
            data: { "number_of_posts": "10", "from_date": from_date, "to_date": to_date },
            success: function(data) {
                // Populate modal here
                logs = JSON.parse(data);

                $('.list-log-item').remove();

                for(var i=0; i<logs.length; i++){
                    $('.list-logs').append('<li class="list-group-item list-log-item">' + logs[i] + '</li>')
                }
            }
        });
    }

    // Add date filter
    function add_date_filter() {
        
        // Set a bool that will determine if `from` and `to` values are set
        from_date_set = true;
        to_date_set = true;

        // Load `from` fields into vars for more intuitive processing
        from_year = $('.from-date-year option:selected').text();
        from_month = $('.from-date-month option:selected').text();
        from_day = $('.from-date-day option:selected').text();
        from_hour = $('.from-date-hour option:selected').text();
        from_minute = $('.from-date-minute option:selected').text();

        // Load `to` fields into vars for more intuitive processing
        to_year = $('.to-date-year option:selected').text();
        to_month = $('.to-date-month option:selected').text();
        to_day = $('.to-date-day option:selected').text();
        to_hour = $('.to-date-hour option:selected').text();
        to_minute = $('.to-date-minute option:selected').text();

        // All `from` values must be set (check that they are ints). If even one isn't, set bool to false.
        if(from_month == 'Month') { from_date_set = false; }
        if(from_day == 'Day') { from_date_set = false; }
        if(from_year == 'Year') { from_date_set = false; }
        if(from_hour == 'Hour') { from_date_set = false; }
        if(from_minute == 'Minute') { from_date_set = false; }

        // All `to` values must be set (check that they are numbers). If even one isn't, set bool to false.
        if(to_month == 'Month') { to_date_set = false; }
        if(to_day == 'Day') { to_date_set = false; }
        if(to_year == 'Year') { to_date_set = false; }
        if(to_hour == 'Hour') { to_date_set = false; }
        if(to_minute == 'Minute') { to_date_set = false; }

        // If all `from` fields are filled out, load them into an array
        if(from_date_set){
            var from_datetime = {"values": [parseInt(from_year), parseInt(from_month), parseInt(from_day), parseInt(from_hour), parseInt(from_minute)]};
        } else {
            var from_datetime = false;
        }

        // If all `to` fields are filled out, construct the `to_datetime` variable
        if(to_date_set){
            var to_datetime = {"values": [parseInt(to_year), parseInt(to_month), parseInt(to_day), parseInt(to_hour), parseInt(to_minute)]};
        } else {
            var to_datetime = false;
        }

        // Send the values to the display_logs function
        display_logs('', from_datetime, to_datetime);
    }

    // Reset date filter
    function reset_date_filter() {

        // Change all the select values to their defaults
        $('.from-date-year').val('Year');
        $('.from-date-month').val('Month');
        $('.from-date-day').val('Day');
        $('.from-date-hour').val('Hour');
        $('.from-date-minute').val('Minute');

        $('.to-date-year').val('Year');
        $('.to-date-month').val('Month');
        $('.to-date-day').val('Day');
        $('.to-date-hour').val('Hour');
        $('.to-date-minute').val('Minute');

        // Remove any filters from the logs
        display_logs();
    }

    // Email logs to recipient
    function email_logs() {

        var logs = [];

        $.each($('.list-logs').children(), function(){
            logs.push($(this).text());
        });

        // Prepare the data for transfer via JSON
        logs = JSON.stringify(logs);

        // Get the email address
        var addresses = $('#inputEmail').val();

        // Send a mail request to main.py
        $.ajax({
            type: "POST",
            url: "/email-logs",
            data: { "addresses" : addresses, "logs": logs},
            success: function(data) {
                var status = JSON.parse(data);
                
                switch(status) {
                    case 'invalid':
                        // Place red border around input box
                        $('.email-logs-form').removeClass('has-success');
                        $('.email-logs-form').addClass('has-error');
                        
                        // Place error message under input box
                        $('.status-message').remove();
                        $('.email-logs-form').append('<p class="status-message error-message">Invalid email address</p>');
                        break;
                    case 'sent':
                        // Place green border around input box
                        $('.email-logs-form').removeClass('has-error');
                        $('.email-logs-form').addClass('has-success');

                        // Place success message under input box
                        $('.status-message').remove();
                        $('.email-logs-form').append('<p class="status-message success-message">Email sent!</p>');
                        break;
                }
            }
        });
    }
});
