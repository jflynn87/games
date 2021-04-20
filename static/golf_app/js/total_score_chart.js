$(document).ready(function () {
    console.log('connected')
    fetch("/golf_app/total_score_chart_api/" + $('#season_id').text(),
    {method: "GET",
    })
  .then((response) => response.json())
  .then((responseJSON) => {
    json_data =  responseJSON
    console.log(json_data)
    var ctx = document.getElementById('trend_chart')

    var ds = []
    var colors = ['aqua', 'blue', 'red', 'purple', 'orange', 'green', 'lightgreen', 'yellow', 'pink', 'black', 'gray']
    var i = 0
    $.each(json_data.data, function(user, stats) {

        //ds = ds + "{label: '" + user + "', data: [" + stats + "]},"
        if (user != $('#user').text())
        {ds.push({label: user, backgroundColor: colors[i], borderColor: colors[i], data: stats, hidden: true})}
        else {ds.push({label: user, backgroundColor: colors[i], borderColor: colors[i], data: stats})}
        i ++;
    })
    
    //ds = ds + ']'

    //ds = [{label: 'john', data: [-167,-265,-393,-355,-418,-410,-557,-699,-652,-633,-678,-698,-645,-574,-445,-603,-746,-835,-890,-851,-872,-589,-569,-557,-836,-1067,-1013]},{label: 'jcarl62', data: [-231,-358,-508,-409,-497,-663,-798,-896,-925,-1016,-1079,-1095,-1035,-1019,-962,-1078,-1152,-1099,-1224,-1087,-1116,-1018,-953,-875,-946,-1119,-1080]},{label: 'BigDipper', data: [-110,-15,-90,-110,-174,-191,-410,-472,-336,-357,-481,-373,-361,-379,-131,-323,-389,-381,-414,-153,-286,-170,-163,-118,-259,-435,-369]},{label: 'ryosuke', data: [-145,-206,-343,-193,-334,-449,-629,-678,-678,-718,-695,-630,-487,-530,-487,-615,-751,-595,-717,-635,-669,-560,-590,-367,-721,-939,-852]},{label: 'shishmeister', data: [-168,-284,-454,-458,-530,-679,-877,-1020,-997,-772,-856,-839,-844,-917,-927,-1044,-1172,-1201,-1275,-1262,-1242,-1187,-1009,-1017,-1110,-1289,-1296]},{label: 'JoeLong', data: [-114,-241,-382,-388,-471,-473,-522,-632,-617,-632,-661,-744,-646,-642,-595,-579,-578,-688,-816,-737,-722,-544,-526,-534,-778,-954,-921]},{label: 'Laroqm', data: [-225,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]},{label: 'Taka', data: [-130,-277,-490,-441,-562,-763,-700,-870,-770,-854,-940,-906,-923,-909,-738,-918,-1080,-1174,-1404,-1424,-1372,-1386,-1382,-1361,-1377,-1546,-1484]},{label: 'Sam36', data: [0,-198,-348,-198,-295,-293,-365,-463,-521,-554,-443,-494,-376,-291,-209,-427,-520,-507,-542,-533,-715,-570,-519,-413,-637,-797,-782]},{label: 'j_beningufirudo', data: [-231,-338,-463,-416,-514,-521,-575,-529,-466,-605,-551,-468,-485,-538,-488,-629,-769,-872,-997,-905,-923,-816,-696,-651,-907,-1078,-1000]},]

    console.log('ds', ds)
    // var ds = [{
    //     label: "Mark",
    //     backgroundColor: 'red',
    //     borderColor: 'red',
    //     data: [0, 10, 5, 29],
    //             },
    //     {
    //     label: "John",
    //     backgroundColor: 'blue',
    //     borderColor: 'blue',
    //     data: [0, 120, 5, 229],
    //                         },                
    
    // ]

    var data = {
        labels: json_data.labels,
        datasets: ds,
    }

    const config = {type: 'line', 
                    data,
                    options: {
                        plugins: {
                            title: {
                                display: true,
                                text: 'Trend Analysis - click name to toggle inclusion in chart'
                            }
                        }
            
                    }}



    var myChart = new Chart(ctx, 
        config

    )
    $('#chart_status_msg').hide()
  })
})