$(document).ready(function(){get_spreads()})
function get_spreads(){console.log('getting spreads')
$('#status').text('updating spreads ....').attr('class','status')
fetch("/fb_app/get_spreads/"+$('#week_key').text(),{method:"GET",}).then((response)=>response.json()).then((responseJSON)=>{json=$.parseJSON(responseJSON)
console.log(json)
for(i=0;i<json.length;++i){console.log(json[i][0])
row=$('tr[name='+json[i][0]+']')
$('td',row).each(function(){if($(this).prop('id').startsWith('spread')){$(this).html(json[i][5])}
else if($(this).prop('id').startsWith('fav')){$(this).html(json[i][1]+"<span class='record'>"+json[i][2]+"</span>")}
else if($(this).prop('id').startsWith('dog')){$(this).html(json[i][3]+"<span class='record'>"+json[i][4]+"</span>")}})}
var months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
now=new Date()
console.log(now)
$('#status').text('spreads updated: '+now).attr('class','updated-status')})};function get_team_name(team_id){var team_list={}
teams=document.getElementById('teams')
for(var i=1;i<=teams.rows.length;i++){team_list[document.getElementById('team_id'+i).innerHTML]=document.getElementById('team_nfl_abbr'+i).innerHTML;};return team_list[team_id]};function get_game_id(team_name){var game_list={}
games=document.getElementById('game_tbl')
for(var j=1;j<=games.rows.length;j++){game_list[$.trim($('#fav'+j).text().split("(")[0].toUpperCase())]='game'+j
game_list[$.trim($('#dog'+j).text().split("(")[0].toUpperCase())]='game'+j}
return game_list[team_name]};$(document).ready(function(){$('#pickstbl').on('change',$("select[id^='id_form_']"),function(){mark_picks()})})
function mark_picks(){game=document.getElementById('game_tbl')
for(g=1;g<=game.rows.length;g++){document.getElementById('game'+g).style='none';}
picks=document.getElementById('pickstbl')
var pick_list=[]
for(p=1;p<=picks.rows.length;p++){pick_list.push($('#pick'+(17-p)).children().children("option").filter(":selected").text())}
for(var k=0;k<pick_list.length;k++){if(pick_list[k]!='---------'){var game_id=get_game_id(pick_list[k]);game=document.getElementById(game_id)
game.style.background='yellow';}}};function validate(){$('#pick_form').attr('onsubmit','return true')
picks=document.getElementById('pickstbl')
var pick_list=[]
for(p=1;p<=picks.rows.length;p++){if(document.getElementById('pick'+(17-p)).children[0].value==''){var missing_picks=true
break}}
if(missing_picks){alert('Missing Picks, please select one team per game')
$('#pick_form').attr('onsubmit','return false');}};$(document).ready(function(){$("#week-list").change(function(){console.log('caught click',$('#week-list').val())
if($('#week-list').val()!=$('#week_key')){console.log($(this).val())
$('#status').text('changing week ....').attr('class','status')
$('#favs').hide()
$('#gamesect').hide()
$('#picksect').hide()
$(this).removeAttr('selected')
location.href=$('#week-list').val()+'/'}})})
$(document).ready(function(){console.log('get weeks')
fetch("/fb_app/get_weeks/",{method:"GET",}).then((response)=>response.json()).then((responseJSON)=>{weeks=$.parseJSON(responseJSON)
console.log(weeks)
$.each(weeks,function(i){console.log('week: ',weeks[i]['fields']['week'])
if(weeks[i]['pk']!=$('#week_key').text()){console.log(weeks[i]['pk'],$('#week_key').text())
$('#week-list').append('<option value=/fb_app/games_list/'+weeks[i]['pk']+'>'+weeks[i]['fields']['week']+'</option>')}})})});