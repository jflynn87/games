// $(document).ready(function() {
//     table = document.getElementById('field_table')
//     for (var i=1; i < table.rows.length; i++) {
//     //console.log(table.rows[i].children[1].id)
//     fetch("/golf_app/get_group/" + table.rows[i].children[1].id,
//     {method: "GET",
//     })
//   .then((response) => response.json())
//   .then((responseJSON) => {
//     field_data = responseJSON
//     $('#' + field_data.field).find('#id_group').val(field_data.group)
    
//   })
// }
// })
