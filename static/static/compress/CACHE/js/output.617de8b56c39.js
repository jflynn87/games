$(document).ready(function(){start=new Date()
$.ajax({type:"GET",url:"/golf_app/get_info/",dataType:'json',data:{'tournament':$('#tournament_key').text()},success:function(json){info=$.parseJSON((json))
buildHeader()
groups=[]
$.each($('#groups_list li'),function(i,g){groups.push(g.innerText)})
var fn=function wrapper(g){return new Promise(resolve=>resolve(build_field(g,info)));};var actions=groups.map(fn)
var results=Promise.all(actions)
results.then((()=>{$.getScript('/static/golf_app/js/field.js')
$('#field_sect form').append('<div id=bottom_sect class=field_stats_display></div>')
$('#bottom_sect').append('<div id=bottom class=field_stats_display>'+'<div id=stats-dtl-toggle>'+'<h5>Hide Stats <i class="fa fa-minus-circle show" style="color:lightblue"></i></h5>'+'</div>'+'<div id=pick-status></div>'+'<div id=grp_6_buttons class=grp_6_buttons>'+'<p id=jump_to style="background-color:lightgray; color:white; font-weight:bold;"> Jump to: '+'</p>'+'</div>'+'<input id=sub_button type="submit" class="btn btn-secondary" value="Submit Picks" disabled>')
$.each(info,function(group,picks){if(group!="total"){$('#jump_to').append('<a href=#tbl-group-'+group+'>'+group+'</a>'+' ')}})
$('#grp_6_buttons').append('<button id=show_6_button class="btn btn-primary btn-group-sm">My G-6 Picks</button>')
$('#pick_form').on('submit',function(event){event.preventDefault();console.log("form submitted!")
create_post();});$('#show_6_button').on('click',function(eve){eve.preventDefault();selected=[]
$.each($('input[name=group-6'+']:checked'),function(){selected.push($(this).parent().attr('id').replace('playerInfo',''))})
console.log(selected)
table=$('#tbl-group-6')
if($('#show_6_button').html()=='All Group 6'){$('input[name=group-6'+']').parent().parent().parent().prop('hidden',false)
$('#show_6_button').html('My Picks G-6')}
else{$('input[name=group-6'+']').parent().parent().parent().prop('hidden',true)
$('input[name=group-6'+']:checked').parent().parent().parent().prop('hidden',false)
$('#show_6_button').html('All Group 6')}
window.location.href='#tbl-group-6'})
checkStarted()}))}})})
function build_field(g,info){return new Promise(function(resolve,reject){$('#field_sect #pick_form').append('<table id=tbl-group-'+g+' class=table> \
                                <thead class=total_score> <th> Group: '+g+'</th> </thead>'+'</table>')
fetch("/golf_app/get_prior_result/",{method:"POST",headers:{'Accept':'application/json','Content-Type':'application/json','X-CSRFToken':$.cookie('csrftoken')},body:JSON.stringify({'tournament_key':$('#tournament_key').text(),'golfer_list':[],'group':g})}).then((response)=>response.json()).then((responseJSON)=>{data=responseJSON
console.log('data',data)
$.each(data,function(i,field){picks=info[field.group.number]
if(picks==1){input_type='radio'
input_class='my-radio'}
else
{input_type='checkbox'
input_class='my-checkbox'}
$('#tbl-group-'+field.group.number.toString()).append('<table id=player-'+field.golfer.espn_number+'-div style="width:100%;"></table>')
const frag=new DocumentFragment()
let field_row=document.createElement('tr')
let stats_row=document.createElement('tr')
let golfer=document.createElement('td')
golfer.id='playerInfo'+field.golfer.espn_number
if(field.withdrawn){golfer.innerHTML='WD'}
else if(!field.started||field.tournament.late_picks){let inputA=document.createElement('input');inputA.type='hidden';inputA.name="csrfmiddlewaretoken";inputA.value=$.cookie('csrftoken')
let inputB=document.createElement('input');inputB.id=field.id
inputB.type=input_type
inputB.classList.add(input_class)
inputB.name="group-"+field.group.number
inputB.value=field.id
golfer.append(inputA)
golfer.append(inputB)
const player_row_class='top_row'}
else if(field.started){golfer.innerHTML='Started'}
else{golfer.innerHTML='Problem'}
img=document.createElement('img')
img.src=field.golfer.pic_link
flag=document.createElement('img')
flag.src=field.golfer.flag_link
google=document.createElement('a')
google.href='https://www.google.com/search?q='+field.playerName
google.innerHTML=" Google"
espn=document.createElement('a')
espn.href=field.espn_link
espn.innerHTML="/ESPN"
pga=document.createElement('a')
pga.href=field.pga_link
pga.innerHTML="/PGA"
golfer.append(img)
golfer.innerHTML=golfer.innerHTML+field.playerName+' '
golfer.append(flag)
golfer.append(google)
golfer.append(espn)
golfer.append(pga)
frag.appendChild(golfer)
document.getElementById('player-'+field.golfer.espn_number+'-div').appendChild(frag)
document.getElementById('player-'+field.golfer.espn_number+'-div').classList.add(player_row_class)
x
$('#player-'+field.golfer.espn_number+'-row').append('<td id=playerInfo'+field.golfer.espn_number+'>'+
(field.started?'Started':!field.withdrawn?'<input type="hidden" name="csrfmiddlewaretoken" value='+$.cookie('csrftoken')+'>'+'<input id='+field.id+' type='+input_type+' class='+input_class+' name=group-'+field.group.number+' value='+field.id+' disabled>':'WD')+'<img src='+field.golfer.pic_link+' style="max-height:125px; alt="">'+field.playerName+' '+'<img src='+field.golfer.flag_link+' alt="">'+'<a href="https://www.google.com/search?q='+field.playerName+'" target="_blank" style="padding-left: 1em;">Google</a> / '+'<a href='+field.espn_link+' target="_blank">ESPN</a> / '+'<a href='+field.pga_link+' target="_blank">PGA</a>'+'</td>')
$('#player-'+field.golfer.espn_number+'-div').append('<tr id=stats-row-'+field.golfer.espn_number+' class="stats_row" >'+'<td>'+'<table id=stats'+field.golfer.espn_number+' class="table stats-row">'+'<tr style=background-color:lightblue;>'+'<th colspan=2>Current OWGR</th>'+'<th colspan=2>Last Week OWGR</th>'+'<th colspan=2>Last Season OWGR</th>'+'<th colspan=2>FedEx Cup</th>'+'</tr>'+'<tr>'+'<td colspan=2>'+field.currentWGR+'</td>'+'<td colspan=2>'+field.sow_WGR+'</td>'+'<td colspan=2>'+field.soy_WGR+'</td>'+'<td colspan=2>rank: '+field.season_stats.fed_ex_rank+'; points:'+field.season_stats.fed_ex_points+'</td>'+'</tr>'+'<tr class=stats_row>'+'<th colspan=2>Handicap</th>'+'<th colspan=2>This event last year</th>'+'<th colspan=4>Recent Form</th>'+'</tr>'+'<tr>'+'<td colspan=2>'+field.handi+'</td>'+'<td colspan=2>'+field.prior_year+'</td>'+'<td colspan=3 id=recent'+field.golfer.espn_number+'> </td>'+'</tr>'+'<tr class=stats_row>'+'<th colspan=8>Season Stats</th>'+'</tr>'+'<tr>'+'<td>Played</td>'+'<td>Won</td>'+'<td>2-10</td>'+'<td>11-29</td>'+'<td>30-49</td>'+'<td>> 50</td>'+'<td>Cuts</td>'+'</tr>'+'<tr>'+'<td>'+field.season_stats.played+'</td>'+'<td>'+field.season_stats.won+'</td>'+'<td>'+field.season_stats.top10+'</td>'+'<td>'+field.season_stats.bet11_29+'</td>'+'<td>'+field.season_stats.bet30_49+'</td>'+'<td>'+field.season_stats.over50+'</td>'+'<td>'+field.season_stats.cuts+'</td>'+'<td></td>'+'</tr>'+'</table>'+'</td>'+'</tr>')
formatSG(field)
$('input#'+field.id).on('change',function(evt){$('#pick-status').empty()
get_info(info,this)})
ranks=''
$.each(field.recent,function(i,rank){ranks+=rank.rank+', '})
var items=''
$.each(field.recent,function(i,rank){items+=rank.name+': '+rank.rank+'\n'})
$('#recent'+field.golfer.espn_number).html('<p>'+ranks+'<span> <a id=tt-recent'+field.golfer.espn_number+' data-toggle="tooltip" html="true" > <i class="fa fa-info-circle" style="color:blue"></i> </a> </span> </p>')
$('#tt-recent'+field.golfer.espn_number+'[data-toggle="tooltip"]').tooltip({trigger:"hover",delay:{"show":400,"hide":800},"title":items})
get_picks_data(field).then(resolve())})})})}
function formatSG(field){$('#stats'+field.golfer.espn_number).append('<tr style=background-color:lightblue;><th colspan=8>Shots Gained Stats</th></tr>')
try{$('#stats'+field.golfer.espn_number).append('<tr><td>Off Tee Rank</td> <td>Off Tee</td> <td>Approach Rank</td> <td>Approach</td><td>Around Green Rank</td><td>Around Green</td> <td>Putting Rank</td> <td>Putting</td></tr>'+'<tr>'+'<td>'+(field.season_stats.off_tee.rank||'n/a')+'</td>'+'<td>'+field.season_stats.off_tee.average+'</td>'+'<td>'+field.season_stats.approach_green.rank+'</td>'+'<td>'+field.season_stats.approach_green.average+'</td>'+'<td>'+field.season_stats.around_green.rank+'</td>'+'<td>'+field.season_stats.around_green.average+'</td>'+'<td>'+field.season_stats.putting.rank+'</td>'+'<td>'+field.season_stats.putting.average+'</td>')}
catch(e){$('#stats'+field.golfer.espn_number).append('<tr><td>No Stats Available</td>')}}
function checkStarted(){fetch("/golf_app/started/",{method:"POST",headers:{'Accept':'application/json','Content-Type':'application/json','X-CSRFToken':$.cookie('csrftoken')},body:JSON.stringify({'key':$('#tournament_key').text(),})}).then((response)=>response.json()).then((responseJSON)=>{started=$.parseJSON(responseJSON)
console.log('started ',started,started.started,started.late_picks)
if(started.started&&!started.late_picks){$("#make_picks").attr('hidden','')
$('#too_late').removeAttr('hidden')
$('#sub_button').remove()}
else{$('#random_btn').removeAttr('disabled').attr('class','btn btn-primary');}})}
function buildHeader(){$('#top_sect').append('<div id=make_picks><br> <p>Please make 1 pick for each group below</p>'+'<form id="random_form" name="random_form" method="post">'+'<input type="hidden" name="csrfmiddlewaretoken" value='+$.cookie('csrftoken')+'>'+'<p>or click for random picks  <input id=random_btn type="submit" class="btn btn-secondary" value="Random" disabled> </p>'+'</form>')
$('#top_sect').append('<div id=too_late hidden><br> <p>Tournament Started, too late for picks</p></div>')
$('#top_sect').append('<span style="float: right;" >'+'<a href="#" id="download_excel" >'+'<i class="fas fa-file-download" title="Download Excel" data-toggle="tooltip"> Download Excel</i>'+'</a>'+'</span>')
$('#top_sect').append('<br> <div id=stats-dtl-toggle>'+'<h5>Hide Stats <i class="fa fa-minus-circle show" style="color:lightblue"></i></h5>'+'<br></div>')
$('#field_sect').append('<form id=pick_form method=post></form>')
if($('#pga_t_num').text()==999){console.log('add countries here')
$('#field_sect #pick_form').append('<table id=mens_countries_picks'+" class=table> \
                                        <thead class=total_score> <th> Men's Medal Countries"+'</th> </thead>'+'</table>')
$('#mens_countries_picks').append('<tr><td>Pick 3 countries, -50 for gold, -35 for silver, -20 for bronze.  Add +5 for each golfer above 1 per country.</td></tr>')
$('#field_sect #pick_form').append('<table id=womens_countries_picks'+" class=table> \
                                        <thead class=total_score> <th> Women's Medal Countries"+'</th> </thead>'+'</table>')
$('#womens_countries_picks').append('<tr><td>Pick 3 countries, -50 for gold, -35 for silver, -20 for bronze.  Add +5 for each golfer above 1 per country.</td></tr>')
fetch("/golf_app/get_country_counts/",{method:"GET",}).then((response)=>response.json()).then((responseJSON)=>{data=responseJSON
console.log('countries: ',data)
formatMenMedals(data)
formatWomenMedals(data)})}
$('#random_form').on('submit',function(event){event.preventDefault();console.log("random submitted!")
create_post_random();});}
function create_post(){toggle_submitting()
checked=$('input:checked')
pick_list=[]
men_countries=[]
women_countries=[]
men_countries.push($('#men_1_country').val(),$('#men_2_country').val(),$('#men_3_country').val())
women_countries.push($('#women_1_country').val(),$('#women_2_country').val(),$('#women_3_country').val())
$.each(checked,function(i,pick){pick_list.push(pick.value)})
console.log(pick_list)
fetch("/golf_app/new_field_list/",{method:"POST",headers:{'Accept':'application/json','Content-Type':'application/json','X-CSRFToken':$.cookie('csrftoken')},body:JSON.stringify({'key':$('#tournament_key').text(),'pick_list':pick_list,'men_countries':men_countries,'women_countries':women_countries,})}).then((response)=>response.json()).then((responseJSON)=>{d=responseJSON
if(d.status==1){window.location=d.url}
else{console.log(d.message)
$('#error_msg').text(d.message).addClass('alert alert-danger')
window.scrollTo(0,0);}
console.log(d)})}
function create_post_random(){toggle_submitting()
pick_list=[]
pick_list.push('random',)
console.log('pick list',pick_list)
fetch("/golf_app/new_field_list/",{method:"POST",headers:{'Accept':'application/json','Content-Type':'application/json','X-CSRFToken':$.cookie('csrftoken')},body:JSON.stringify({'key':$('#tournament_key').text(),'pick_list':pick_list,})}).then((response)=>response.json()).then((responseJSON)=>{d=responseJSON
if(d.status==1){window.location=d.url}
else{console.log(d.message)
$('#error_msg').text(d.message).addClass('alert alert-danger')
window.scrollTo(0,0);}
console.log(d)})}
function toggle_submitting(){$('#sub_button').prop('disabled','true')
$('#sub_button').prop('value','Submitting....')
$('#random_btn').prop('disabled','true')
$('#random_btn').prop('value','Submitting....')
$('#top_sect').append('<p class=status style="text-align:center;"> Submitting picks, one moment....')
$('#bottom').append('<p class=status style="text-align:center;"> Submitting picks, one moment....')}
function formatMenMedals(data){$('#mens_countries_picks').append('<tr><td>Pick 1:  <select id=men_1_country> </select><td> </tr>')
$('#mens_countries_picks').append('<tr><td>Pick 2:  <select id=men_2_country> </select><td> </tr>')
$('#mens_countries_picks').append('<tr><td>Pick 3:  <select id=men_3_country> </select><td> </tr>')
$('#mens_countries_picks').on('change',function(evt){$('#pick-status').empty()
get_info(info,null)})
$.each(data.men,function(country,count){$('#men_1_country').append('<option value='+country+'>'+country+': '+count+'</option>')
$('#men_2_country').append('<option value='+country+'>'+country+': '+count+'</option>')
$('#men_3_country').append('<option value='+country+'>'+country+': '+count+'</option>')})}
function formatWomenMedals(date){$('#womens_countries_picks').append('<tr><td>Pick 1:  <select id=women_1_country> </select><td> </tr>')
$('#womens_countries_picks').append('<tr><td>Pick 2:  <select id=women_2_country> </select><td> </tr>')
$('#womens_countries_picks').append('<tr><td>Pick 3:  <select id=women_3_country> </select><td> </tr>')
$('#womens_countries_picks').on('change',function(evt){$('#pick-status').empty()
get_info(info,null)})
$.each(data.women,function(country,count){$('#women_1_country').append('<option value='+country+'>'+country+': '+count+'</option>')
$('#women_2_country').append('<option value='+country+'>'+country+': '+count+'</option>')
$('#women_3_country').append('<option value='+country+'>'+country+': '+count+'</option>')})};