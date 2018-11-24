$(function() {

    $("#searchy").on("click", function(e) {
        $("#loading").show();

        e.preventDefault();
        var searchVal = $(".form-control").val();

        if (searchVal != "") {

            $.ajax({
                "url" : "/get-tags-from-string-contained?instring=" + searchVal + "&maxbackoffsec=200",
                "type" : "GET",

                beforeSend: function() {
                },

                error: function() {
                   alert("Error");
                },

                success: function(response) {
                   $("#welc-banner").hide();
                   $("#loading").hide();

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
                            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                        },
                        plotOptions: {
                            pie: {
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: false,
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
                            data: response.chartData
                        }]
                    });

                    if ($.fn.DataTable.isDataTable("#list-table") ) {
                        $('#list-table').DataTable().destroy();
                    }

                    $('#list-table').DataTable({
                        "order": [[ 1, "desc" ]],
                        data: response.tableData,
                        "pageLength": 8,
                        columns: [
                            { title: "Tag Name" },
                            { title: "Question Count" }
                        ]
                    });
                }
            });
        } else {
            $("#loading").hide();
        }
    });

    $("#welc-banner").fadeIn("slow");

    $("#mine-devs").on("click", function(e) {
        $("#loading").show();

        e.preventDefault();
        var searchVal = $(".form-control").val();

        if (searchVal != "") {
            $.ajax({

                "url" : "/get-dev-profile?tagname=" + searchVal,
                "type" : "GET",

                error: function() {
                   alert("Error");
                },

                success: function(response) {
                    $("#welc-banner").hide();
                    $("#loading").hide();

                    Highcharts.chart('dev-tags', {
                        chart: {
                            type: 'column'
                        },
                        title: {
                            text: 'Top Tags by Devs Using: ' + searchVal
                        },
                        subtitle: {
                            text: ''
                        },
                        colors: ['#ff652f'],
                        xAxis: {
                            type: 'category',
                            labels: {
                                rotation: -45,
                                style: {
                                    fontSize: '13px',
                                    fontFamily: 'Verdana, sans-serif'
                                }
                            }
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: ' Total Usage Count'
                            }
                        },
                        legend: {
                            enabled: false
                        },
                        tooltip: {
                            pointFormat: 'Count: <b>{point.y:.1f}</b>'
                        },
                        series: [{
                            name: 'Tag Counts',
                            data: response.tagChartData,
                            dataLabels: {
                                enabled: false,
                                rotation: -90,
                                color: '#FFFFFF',
                                align: 'right',
                                format: '{point.y:.1f}', // one decimal
                                y: 10, // 10 pixels down from the top
                                style: {
                                    fontSize: '13px',
                                    fontFamily: 'Verdana, sans-serif'
                                }
                            }
                        }]
                    });

                    Highcharts.chart('dev-rep', {
                        title: {
                            text: 'Dev Reputation Distribution'
                        },
                        xAxis: [{
                            title: { text: 'Dev Number' },
                            alignTicks: false
                        }, {
                            title: { text: 'Bin' },
                            alignTicks: false,
                            opposite: true
                        }],

                        yAxis: [{
                            title: { text: 'Reputation' }
                        }, {
                            title: { text: 'Frequency' },
                            opposite: true
                        }],

                        series: [{
                            name: 'Histogram',
                            type: 'histogram',
                            color: '#14a76c',
                            xAxis: 1,
                            yAxis: 1,
                            baseSeries: 's1',
                            zIndex: -1
                        }, {
                            name: 'Data',
                            type: 'scatter',
                            color: '#272727',
                            data: response.repDistData,
                            id: 's1',
                            marker: {
                                radius: 1.5
                            }
                        }]
                    });

                    if ($.fn.DataTable.isDataTable("#tag-list-table") ) {
                        $('#tag-list-table').DataTable().destroy();
                    }

                    $('#tag-list-table').DataTable({
                        "order": [[ 1, "desc" ]],
                        data: response.tagTableData,
                        "pageLength": 8,
                        columns: [
                            { title: "Tag Name" },
                            { title: "Usage Count" }
                        ]
                    });
                }

            })
        } else {
            $("#loading").hide();
        }


    });

});