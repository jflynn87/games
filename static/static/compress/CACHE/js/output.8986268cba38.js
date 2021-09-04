$(document).ready(function(){color()})
function color(){$('td.ranks').each(function(index){if($(this).text()=='1'){$(this).css("background-color","#ff3333");}
else if($(this).text()=='2'){$(this).css("background-color","#ccebff");}
else if($(this).text()=='3'){$(this).css("background-color","#ffff99");}
else{$(this).css("background-color","transparent")}});};