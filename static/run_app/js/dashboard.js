$( document ).ready(function() {
    $('td.dist').each(function( index ) {
          if($( this ).text() > 500){
             $(this).css("background-color","#ff3333");
}
    });
    $('td.change').each(function( index ) {
          if($( this ).text() < 0){
             $(this).css("color","#ff3333");}
             $(this)[0].innerHTML = $(this)[0].innerHTML + '%'


    });
});
