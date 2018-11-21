$(function() {

    $("#searchy").on("click", function(e) {
        e.preventDefault();
        var searchVal = $(".form-control").val();

        if (searchVal != "") {

            $.ajax({
                "url" : "/get-tags-from-string-contained?instring=" + searchVal + "&maxbackoffsec=200",
                "type" : "GET",

                beforeSend: function() {
                   alert(1);
                },

                error: function() {
                   alert("Error");
                },

                success: function(response) {

                   Highcharts.chart('chart-container', {
                        chart: {
                            plotBackgroundColor: null,
                            plotBorderWidth: null,
                            plotShadow: false,
                            type: 'pie'
                        },
                        title: {
                            text: 'Tag Distribution, total question counts: ' + searchVal
                        },
                        tooltip: {
                            pointFormat: '{series.name}: <b>{point.y:,.0f}</b>'
                        },
                        plotOptions: {
                            pie: {
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: true,
                                    format: '<b>{point.name}</b>: {point.y:,.0f}',
                                    style: {
                                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                                    }
                                }
                            }
                        },
                        series: [{
                            name: 'Tags',
                            colorByPoint: true,
                            data: response
                        }]
                    });
                }
            });
        } else {

        }
    });
});