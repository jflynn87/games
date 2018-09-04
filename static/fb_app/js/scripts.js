function allowDrop(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "copy";
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
    ev.dataTransfer.dropEffect = "copy";
}

function drop(ev) {
  ev.preventDefault();
  var data=ev.dataTransfer.getData("text");

  origData = ev
  /* If you use DOM manipulation functions, their default behaviour it not to
     copy but to alter and move elements. By appending a ".cloneNode(true)",
     you will not move the original element, but create a copy. */
  var nodeCopy = document.getElementById(data).cloneNode(true);

  origId = nodeCopy.id
  nodeCopy.id = "p" + nodeCopy.id; /* We cannot use the same ID */
  ev.target.appendChild(nodeCopy);
  nodeCopy.id = origId;



  markGamePicked(nodeCopy, ev.target.id);

  }

function markGamePicked(nodeCopy, targetID) {

  team = document.getElementById(nodeCopy.id)
  if (nodeCopy.id[0] =="f")
    {  team2ID = 'dog' + nodeCopy.id.slice(3); }
  else if (nodeCopy.id[0] == "d")
    {  team2ID = "fav" + nodeCopy.id.slice(3); }

  pick = document.getElementById(targetID)


  team2 = document.getElementById(team2ID);

  team.style.color = 'red';
  team.style.textDecorationLine = 'line-through';
  team.draggable = false;
  team2.style.textDecorationLine = 'line-through';
  team2.draggable = false;

  pick.ondragover = false;
  pick.style.background = ''

  //pick_list_id = 'pick_list' + targetID.slice(4)
  //document.getElementById(pick_list_id).value = document.getElementById(targetID).children[0].innerHTML

}


function submitpicks() {

       console.log("submit");
       var game_cnt = document.getElementById("game_tbl").rows.length
       var i = (16 - game_cnt) +1

       while (i <= 16){
         console.log(i);
         var pick_id = ("pick" + i);
         var pick_list_id = ("pick_list" + i)
         if (typeof document.getElementById(pick_id).children[0] != 'undefined') {
          if (document.getElementById(pick_id).children[0].innerHTML > '')  {
              document.getElementById(pick_list_id).value = document.getElementById(pick_id).children[0].innerHTML
              i++;
              console.log('child');
         }
}
         else if (document.getElementById(pick_id).innerHTML > '') {
              console.log('no child');
              console.log(document.getElementById(pick_id).innerHTML);
              document.getElementById(pick_list_id).value = document.getElementById(pick_id).innerHTML
              i++;

         }
         else {
              console.log("missing pick")
              alert("Missing Picks, please enter a pick for every game")
              break
       };
     };
  };


document.addEventListener("dragenter", function( event ) {
      // highlight potential drop target when the draggable element enters it
      if ( event.target.className == "dropzone" ) {
          event.target.style.background = "#f2dddf";
      }

  }, false);


document.addEventListener("dragleave", function( event ) {
        // reset background of potential drop target when the draggable element leaves it

        if ( event.target.className == "dropzone" ) {
            event.target.style.background = "";
        }

    }, false);



        //event.target.innerHTML = document.getElementById(pick_id).children[0].innerHTML
        //     i++;
        //     console.log(document.getElementById(pick_list_id).innerHtml);
        //   }



$('#pickstbl td').on('dblclick', function(){
  var cell = ('#' + $(this).attr('id'));
  orig_cell =$(this).children()[0];
  $(cell).html("");


  cxl_team = document.getElementById(orig_cell.id)
  if (orig_cell.id[0] =="f")
    {  cxl_team2ID = 'dog' + orig_cell.id.slice(3); }
  else if (orig_cell.id[0] == "d")
    {  cxl_team2ID = "fav" + orig_cell.id.slice(3); }

  console.log($(this[0]));
  pick = document.getElementById($(this).attr('id'));
  pick.setAttribute('ondragover', "allowDrop(event)");


  cxl_team = document.getElementById(orig_cell.id)
  cxl_team.style.color = 'black';
  cxl_team.style.textDecorationLine = 'none';
  cxl_team.draggable = true;

  cxl_team2 = document.getElementById(cxl_team2ID)
  cxl_team2.style.color = 'black';
  cxl_team2.style.textDecorationLine = 'none';
  cxl_team2.draggable = true;

  })


    //       else if (document.getElementById(pick_id) > '') {
    //         pick_list.push(pick_id, document.getElementById(pick_id).innerHTML);
    //         console.log(pick_list);
    //         i++;
    //       }
    //     else {
    //         console.log("missing pick")
    //         alert("Missing Picks, please enter a pick for every game")
    //         break
    //       };
