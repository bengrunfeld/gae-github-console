$(function(){
 
    $('.edit-repo').click(get_data);

    //Pull all relevant data to populate the modal
    function get_data(repo_name){
        
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
                            $('.list-teams').append('<li class="list-group-item teams"><span class="team">' + key + '<span class="permission"> (' + data.teams[key][1] + ')</span>' + '</span><button type="button" class="btn btn-success btn-sm team-btn add-team pull-right" id="' + data.teams[key] + '">Add Team</button></li>');
                        }
                    }

                    // Print out repo teams and the 'edit access' buttons
                    if(data.team_collaborators) {
                        for(var key in data.team_collaborators){
                            permission = data.team_collaborators[key][1]
                            var content = '<li class="list-group-item team_collaborators"><span class="team_collaborator">' + key + '<span class="permission"> (' + data.team_collaborators[key][1] + ')</span>' + '</span>';
                            content += '<button type="button" id="' + data.team_collaborators[key][0] + '" class="close remove-team" aria-hidden="true">&times;</button>';

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

                    //List all Members in the Org
                    if(data.members) {
                        for(var i=0;i<data.members.length;i++){
                            $('.list-members').append('<option class="members" value="' + data.members[i] + '">' + data.members[i] + '</option>');
                        }
                    }

                    bind_events();
                }
            }
        });
    }

    // Bind click events to the buttons
    function bind_events() {
        $('.add-team').click(add_team);
        $('.remove-team').click(remove_team);
        $('.make-admin').click(edit_team);
        $('.make-push').click(edit_team);
        $('.make-pull').click(edit_team);
    }

    // Add a team to a repo
    function add_team() {

        // Get the repo name
        var repo = $('.panel-repo-name').html();

        // Get the team id
        var team_id = $(this).attr('id');

        // Give the team Push Access
        $.ajax({
            type: "POST",
            url: "/add-team",
            data: { "repo" : repo, "team_id" : team_id },
            success: function(data) {
                var repo_name = repo
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

        // Give the team Push Access
        $.ajax({
            type: "POST",
            url: "/remove-team",
            data: { "repo" : repo, "team_id" : team_id },
            success: function(data) {
                var repo_name = repo
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
                var repo_name = repo
                get_data(repo_name);
            }
        });
    }
});
