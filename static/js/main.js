$(function(){

    $('.edit-repo').click(get_data);

    // Bind events
    function bind_events() {
        $('.add-team').click(add_team);
        $('.remove-team').click(remove_team);
        $('.make-admin').click(edit_team);
        $('.make-push').click(edit_team);
        $('.make-pull').click(edit_team);
        $('.list-all-teams').change(change_team);
        $('.add-team-members').click(add_team_members);
    }


    // Not working yet - refactor other code when it works later
    function query(type, url, data, success_func, repo) {
    
        // Send to main.py
        $.ajax({
            type: type,
            url: url,
            data: data,
            success: function(data) {
                success_func(repo);
            }
        });
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
                            $('.list-teams').append('<li class="list-group-item teams"><span class="team">' + key + '<span class="permission"> (' + data.teams[key][1] + ')</span>' + '</span><button type="button" class="btn btn-success btn-sm team-btn add-team pull-right" id="' + data.teams[key] + '" name="' + key + '">Add Team</button></li>');
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
                    for(var i=0;i<team_members.length;i++){
                        $('.list-team-members').append('<li class="list-group-item team-member">' + team_members[i] + '<button class="btn btn-danger btn-sm team-btn make-pull pull-right remove-member" value="' + team_members[i] + '">Remove</button></li>');
                    }
                }

                // Set an event handler for the Remove buttons
                $('.remove-member').click(remove_member);

                // Remove any previous results
                $('.members').remove();

                //List all Members in the Org
                if(all_members) {
                    for(var i=0;i<all_members.length;i++){
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
});
