$( document ).ready(function() { 

/* $(document).on('click', function() { */
  setInterval (function() {(refresh(200000), 200000)}) 
})
function refresh() {
    console.log('js linked') 
        
    // setInterval(function() { 
    
    
    $.ajax({
        type: "GET",
        url: "/fb_app/update_scores/",
        data: {'week' : $('#week').text(), 
               'league': $('#league').text(),
               'season': $('#season').text()
            },
        dataType: 'json',
        /*context: document.body, */
        success: function (json) {
            if ($.parseJSON(json) == 'week not started') {
                console.log('week not started')
            }
            else {
            table = document.getElementById('score-tbl')
            updates = $.parseJSON(json)
           
            for (i = 1; i < table.rows.length; ++i) { 
                game = table.rows[i]
                $('#' + game.id + 'home_score').text(updates[game.id]['home_score'])
                $('#' + game.id + 'away_score').text(updates[game.id]['away_score'])
                $('#' + game.id + 'qtr').text(updates[game.id]['qtr'])
                
                
                if (updates[game.id]['final'] === true) {
                   $('#winners > tbody').find('tr').each(function() {
                    if (typeof($(this).find('input').val()) === 'undefined' && $(this).attr('id')==game.id + 'winners') {
                        console.log('inside if', game.id)
                        $(this).children().remove()
                        $(this).append('<input type="hidden" value=' + updates[game.id]['winner'] + '"' + ' name="winners" />')
                        $(this).append('<td>' + updates[game.id]["winner"] + '</td>')
                   }
                })
                }
            }

            
            var player_list = player_index()
            console.log(updates['losers'])
            
            $('#scores').find('td').each (function(index, text) {
                
                if (index > 0) {
                    $(this).text(updates[player_list[index-1]]['score'])
             
            }}) 
                
            $('#ranks').find('td').each (function(index, text) {
                if (index > 0) {
                $(this).text(updates[player_list[index-1]]['week_rank'])
                $(this).css('background-color', rank_color($(this)))
            }}) 

            $('#proj').find('td').each (function(index, text) {
                if (index > 0) {
                $(this).text(updates[player_list[index-1]]['week_proj'])

            }});

             

            $('#proj_rank').find('td').each (function(index, text) {
                if (index > 0) {
                $(this).text(updates[player_list[index-1]]['week_proj_rank'])
                $(this).css('background-color', rank_color($(this)))
            }}) 

            $('#season_total').find('td').each (function(index, text) {
                if (index > 0) {
                $(this).text(updates[player_list[index-1]]['season_total'])
             
            }}) 

            $('#season_rank').find('td').each (function(index, text) {
                if (index > 0) {
                $(this).text(updates[player_list[index-1]]['season_rank'])
             
            }}) 
            
            $('#picks-tbl tr').each(function(){
                $(this).find('td').each(function(){
                  if ($.inArray($(this).text(), updates['losers']) !== -1) {
                        $(this).css('color', 'red')
                    }
                })
            })
        }
    },
        failure: function (json) {
            console.log('fail')
        }
        })

    
    // , 2000000 })
}



function player_index() {
    var player_list = []
    $('#players').find('th').each (function(index) {
        if (index>0) {
    player_list.push($(this).text())
    }})
    return player_list

  
};                      

function rank_color(field) {

        /* figure out how to import this from ranks */
        if(field.text()== '1'){
            bc = "#ff3333";
        }
        else if (field.text() == '2') {
            bc = "#ccebff";
        }
        else if (field.text() == '3') {
            bc ="#ffff99";
        }
        else {
            bc = 'white'}

        return bc
}

