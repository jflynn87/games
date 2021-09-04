$(document).ready(function(){start=new Date()
$.ajax({type:"GET",url:"/golf_app/get_info/",dataType:'json',data:{'tournament':$('#tournament_key').text()},success:function(json){info=$.parseJSON((json))
buildHeader()
groups=[]
$.each($('#groups_list li'),function(i,g){groups.push(g.innerText)})
var fn=function wrapper(g){return new Promise(resolve=>resolve(build_field(g,info)));};var actions=groups.map(fn)
var results=Promise.all(actions)
results.then((()=>{console.log('getting field js')
$.getScript('/static/golf_app/js/field.js')
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
const frag=new DocumentFragment()
fetch("/golf_app/get_prior_result/",{method:"POST",headers:{'Accept':'application/json','Content-Type':'application/json','X-CSRFToken':$.cookie('csrftoken')},body:JSON.stringify({'tournament_key':$('#tournament_key').text(),'golfer_list':[],'group':g})}).then((response)=>response.json()).then((responseJSON)=>{data=responseJSON
console.log('data group: ',g,data)
data_l=data.length
for(let idx=0;idx<data_l;idx++){field=data[idx]
picks=info[field.group.number]
if(picks==1){input_type='radio'
input_class='my-radio'}
else
{input_type='checkbox'
input_class='my-checkbox'}
$('#tbl-group-'+field.group.number.toString()).append('<table id=player-'+field.golfer.espn_number+'-div style="width:100%;"></table>')
let field_row=document.createElement('tr')
field_row.classList.add('top_row')
let golfer=document.createElement('td')
golfer.id='playerInfo'+field.golfer.espn_number
if(field.withdrawn){golfer.innerHTML='WD'}
else if(!field.started||field.tournament.late_picks){let inputA=document.createElement('input');inputA.type='hidden';inputA.name="csrfmiddlewaretoken";inputA.value=$.cookie('csrftoken')
let inputB=document.createElement('input');inputB.id=field.id
inputB.type=input_type
inputB.classList.add(input_class)
inputB.name="group-"+field.group.number
inputB.value=field.id
inputB.input.addEventListener('change',function(){console.log('click happened!');});golfer.appendChild(inputA)
golfer.appendChild(inputB)}
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
golfer.appendChild(img)
golfer.innerHTML=golfer.innerHTML+field.playerName+' '
golfer.appendChild(flag)
golfer.appendChild(google)
golfer.appendChild(espn)
golfer.appendChild(pga)
field_row.appendChild(golfer)
frag.appendChild(field_row)
let stats_row=document.createElement('tr');stats_row.classList.add('stats_row')
stats_cell=document.createElement('td')
stats_row.appendChild(stats_cell)
let stats_table=document.createElement('table');stats_table.classList.add('table','stats-row')
let rowA_header_fields=['Current OWGR','Last Week OWGR','Last Season OWGR','FedEx Cup']
rowA_field_l=rowA_header_fields.length
rowA_header=document.createElement('tr')
rowA_header_cells=[]
for(let i=0;i<rowA_field_l;i++){let header_field=document.createElement('th')
header_field.innerHTML=rowA_header_fields[i]
header_field.colSpan=2
rowA_header_cells.push(header_field)}
for(let i=0;i<rowA_field_l;i++){rowA_header.append(rowA_header_cells[i])}
rowA_header.classList.add('stats_row')
stats_table.appendChild(rowA_header)
let stats_rowA=document.createElement('tr')
currOWGR=document.createElement('td')
currOWGR.innerHTML=field.currentWGR
currOWGR.colSpan=2
sowOWGR=document.createElement('td')
sowOWGR.innerHTML=field.sow_WGR
sowOWGR.colSpan=2
soyOWGR=document.createElement('td')
soyOWGR.innerHTML=field.soy_WGR
soyOWGR.colSpan=2
fedEx=document.createElement('td')
fedEx.innerHTML='rank: '+field.season_stats.fed_ex_rank+'; points:'+field.season_stats.fed_ex_points
fedEx.colSpan=2
stats_rowA.append(currOWGR)
stats_rowA.append(sowOWGR)
stats_rowA.append(soyOWGR)
stats_rowA.append(fedEx)
stats_table.appendChild(stats_rowA)
let stats_rowB=document.createElement('tr')
let rowB_header_fields=['Handicap','This event last year','Recent Form']
rowB_field_l=rowB_header_fields.length
rowB_header=document.createElement('tr')
rowB_header_cells=[]
for(let i=0;i<rowB_field_l;i++){let header_field=document.createElement('th')
header_field.innerHTML=rowB_header_fields[i]
if(i+1==rowB_field_l){header_field.colSpan=4}
else{header_field.colSpan=2}
rowB_header_cells.push(header_field)}
for(let i=0;i<rowB_field_l;i++){rowB_header.append(rowB_header_cells[i])}
rowB_header.classList.add('stats_row')
handicap=document.createElement('td')
handicap.innerHTML=field.handi
handicap.colSpan=2
prior_year=document.createElement('td')
prior_year.innerHTML=field.prior_year
prior_year.colSpan=2
recent_form=document.createElement('td')
recent_form.id='recent'+field.golfer.espn_number
recent_form.colSpan=4
stats_rowB.append(handicap)
stats_rowB.append(prior_year)
stats_rowB.append(recent_form)
stats_table.appendChild(rowB_header)
stats_table.appendChild(stats_rowB)
let stats_rowC=document.createElement('tr')
let cell=document.createElement('th')
cell.innerHTML='Season Stats'
cell.colSpan=8
cell.classList.add('stats_row')
stats_rowC.appendChild(cell)
stats_table.appendChild(stats_rowC)
let rowD_header=document.createElement('tr')
rowD_header_fields=['Played','Won','2-10','11-29','30-49','50','Cuts']
rowD_field_l=rowD_header_fields.length
rowD_header_cells=[]
for(let i=0;i<rowD_field_l;i++){let header_field=document.createElement('th')
header_field.innerHTML=rowD_header_fields[i]
if(i+1==rowD_field_l){header_field.colSpan=2}
else{header_field.colSpan=1}
rowD_header_cells.push(header_field)}
for(let i=0;i<rowD_field_l;i++){rowD_header.append(rowD_header_cells[i])}
let stats_rowD=document.createElement('tr')
let cellA=document.createElement('td')
cellA.colSpan=1
cellA.innerHTML=field.season_stats.played
stats_rowD.appendChild(cellA)
let cellB=document.createElement('td')
cellB.colSpan=1
cellB.innerHTML=field.season_stats.won
stats_rowD.appendChild(cellB)
let cellC=document.createElement('td')
cellC.colSpan=1
cellC.innerHTML=field.season_stats.top10
stats_rowD.appendChild(cellC)
let cellD=document.createElement('td')
cellD.colSpan=1
cellD.innerHTML=field.season_stats.bet11_29
stats_rowD.appendChild(cellD)
let cellE=document.createElement('td')
cellE.colSpan=1
cellE.innerHTML=field.season_stats.bet30_49
stats_rowD.appendChild(cellE)
let cellF=document.createElement('td')
cellF.colSpan=1
cellF.innerHTML=field.season_stats.over50
stats_rowD.appendChild(cellF)
let cellG=document.createElement('td')
cellG.colSpan=1
cellG.innerHTML=field.season_stats.cuts
stats_rowD.appendChild(cellG)
stats_table.appendChild(rowD_header)
stats_table.appendChild(stats_rowD)
let sg_row=document.createElement('tr')
let sg_cell=document.createElement('th')
sg_cell.innerHTML='Shots Gained Stats'
sg_cell.colSpan=8
sg_cell.classList.add('stats_row')
sg_row.appendChild(sg_cell)
stats_table.appendChild(sg_row)
let rowE_header=document.createElement('tr')
rowE_header_fields=['Off Tee Rank','Off Tee','Approach Rank','Approach','Around Green Rank','Around Green','Putting Rank','Putting']
rowE_field_l=rowE_header_fields.length
rowE_header_cells=[]
for(let i=0;i<rowE_field_l;i++){let header_field=document.createElement('th')
header_field.innerHTML=rowE_header_fields[i]
rowE_header_cells.push(header_field)}
for(let i=0;i<rowE_field_l;i++){rowE_header.append(rowE_header_cells[i])}
let stats_rowE=document.createElement('tr')
let sg_cellA=document.createElement('td')
sg_cellA.innerHTML=field.season_stats.off_tee.rank||'n/a'
stats_rowE.appendChild(sg_cellA)
let sg_cellB=document.createElement('td')
sg_cellB.innerHTML=field.season_stats.off_tee.average
stats_rowE.appendChild(sg_cellB)
let sg_cellC=document.createElement('td')
sg_cellC.innerHTML=field.season_stats.approach_green.rank
stats_rowE.appendChild(sg_cellC)
let sg_cellD=document.createElement('td')
sg_cellD.innerHTML=field.season_stats.approach_green.average
stats_rowE.appendChild(sg_cellD)
let sg_cellE=document.createElement('td')
sg_cellE.innerHTML=field.season_stats.around_green.rank
stats_rowE.appendChild(sg_cellE)
let sg_cellF=document.createElement('td')
sg_cellF.innerHTML=field.season_stats.around_green.average
stats_rowE.appendChild(sg_cellF)
let sg_cellG=document.createElement('td')
sg_cellG.innerHTML=field.season_stats.putting.rank
stats_rowE.appendChild(sg_cellG)
let sg_cellH=document.createElement('td')
sg_cellH.innerHTML=field.season_stats.putting.average
stats_rowE.appendChild(sg_cellH)
stats_table.appendChild(rowE_header)
stats_table.appendChild(stats_rowE)
stats_cell.append(stats_table)
frag.appendChild(stats_row)
ranks=''
$.each(field.recent,function(i,rank){ranks+=rank.rank+', '})
var items=''
$.each(field.recent,function(i,rank){items+=rank.name+': '+rank.rank+'\n'})
$('#recent'+field.golfer.espn_number).html('<p>'+ranks+'<span> <a id=tt-recent'+field.golfer.espn_number+' data-toggle="tooltip" html="true" > <i class="fa fa-info-circle" style="color:blue"></i> </a> </span> </p>')
$('#tt-recent'+field.golfer.espn_number+'[data-toggle="tooltip"]').tooltip({trigger:"hover",delay:{"show":400,"hide":800},"title":items})
resolve()}
document.getElementById('tbl-group-'+g).appendChild(frag);})})}
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