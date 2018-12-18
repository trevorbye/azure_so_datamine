$(function() {
    $("a.main-tool-tip").tooltip();

    $("#searchy").on("click", function(e) {
        $("#loading").show();

        e.preventDefault();
        var searchVal = $(".form-control").val();
        console.log(searchVal)

        if (searchVal != "") {

            $.ajax({
                "url" : "/get-tags-from-string-contained?instring=" + searchVal + "&maxbackoffsec=200",
                "type" : "GET",

                beforeSend: function() {
                },

                error: function() {
                   $("#loading").hide();
                   $("#bad-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
                },

                success: function(response) {
                   if (response.chartData.length == 0) {
                       $("#loading").hide();
                       $("#bad-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
                   } else {
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
                }
            });
        } else {
            $("#loading").hide();
            $("#empty-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
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
                   $("#loading").hide();
                   $("#bad-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
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

                    Highcharts.chart('tag-trend', {
                        chart: {
                            zoomType: 'x'
                        },
                        title: {
                            text: 'Tag Question Count Trend Over Time'
                        },
                        subtitle: {
                            text: document.ontouchstart === undefined ?
                                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
                        },
                        xAxis: {
                            type: 'datetime'
                        },
                        yAxis: {
                            title: {
                                text: 'Question Count'
                            }
                        },
                        legend: {
                            enabled: false
                        },
                        plotOptions: {
                            area: {
                                fillColor: {
                                    linearGradient: {
                                        x1: 0,
                                        y1: 0,
                                        x2: 0,
                                        y2: 1
                                    },
                                    stops: [
                                        [0, Highcharts.getOptions().colors[0]],
                                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                                    ]
                                },
                                marker: {
                                    radius: 2
                                },
                                lineWidth: 1,
                                states: {
                                    hover: {
                                        lineWidth: 1
                                    }
                                },
                                threshold: null
                            }
                        },

                        series: [{
                            type: 'area',
                            name: 'Question Count by Week',
                            data: response.tagTrendData
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
            $("#empty-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
        }


    });

    $("#mine-text").on("click", function(e) {
        $("#loading").show();

        e.preventDefault();
        var searchVal = $(".form-control").val();

        if (searchVal != "") {
            $.ajax({

                "url" : "/get-text-analytics?tagname=" + searchVal,
                "type" : "GET",

                error: function() {
                   $("#loading").hide();
                   $("#bad-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
                },

                success: function(response) {
                    $("#welc-banner").hide();
                    $("#loading").hide();
                    $("#cosine-form").show();

                    if ($.fn.DataTable.isDataTable("#body-word-list") ) {
                        $('#body-word-list').DataTable().destroy();
                    }

                    if ($.fn.DataTable.isDataTable("#msdocs-matrix") ) {
                        $('#msdocs-matrix').DataTable().destroy();
                    }

                    $("#title-1").show();
                    $("#title-2").show();

                    $("#card-item-1").text("Total Questions: " + response.msDocsSummaryStats.totalQuestions);
                    $("#card-item-2").text("Total MSDocs Links: " + response.msDocsSummaryStats.totalLinks);
                    $("#card-item-3").text("Unique MSDocs Links: " + response.msDocsSummaryStats.uniqueLinks);
                    $("#card-item-4").text("Total MSDocs Links as % of Total Questions: " + response.msDocsSummaryStats.linksPercent);
                    $("#summary-stats").show();

                    $('#body-word-list').DataTable({
                        "order": [[ 1, "desc" ]],
                        data: response.bodyWordList,
                        "pageLength": 8,
                        columns: [
                            { title: "Word" },
                            { title: "Usage Count" }
                        ]
                    });

                    $('#msdocs-matrix').DataTable({
                        "order": [[ 2, "desc" ]],
                        data: response.msDocsUriMatrix,
                        "pageLength": 3,
                        columns: [
                            {title: "Full URL",
                             "render": function (data, type, row, meta) {
                                  return '<a href="' + data + '">' + data + '</a>';
                            }
                            },
                            {title: "Article"},
                            {title: "Linked Count"}
                        ]
                    });

                    Highcharts.chart('cosine-matrix', {
                        chart: {
                            type: 'packedbubble',
                            height: '500px',

                        },
                        title: {
                            text: 'Question Title Semantic Groups'
                        },
                        tooltip: {
                            useHTML: true,
                            pointFormat: '<b>{point.name}:</b> {point.y} tot. questions'
                        },
                        plotOptions: {
                            packedbubble: {
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.name}',
                                    filter: {
                                        property: 'y',
                                        operator: '>',
                                        value: 250
                                    },
                                    style: {
                                        color: 'black',
                                        textOutline: 'none',
                                        fontWeight: 'normal'
                                    }
                                },
                                minPointSize: 5
                            }
                        },
                        series: response.cosineSimilarity,
                        responsive: {
                            rules: [{
                                condition: {
                                    maxWidth: 500
                                },
                                chartOptions: {
                                    legend: {
                                        align: 'right',
                                        verticalAlign: 'middle',
                                        layout: 'vertical'
                                    }
                                }
                            }]
                        }
                    });
                }

            })
        } else {
            $("#loading").hide();
            $("#empty-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
        }

    });

    $("#refresh-cosine").on("click", function(e) {

        e.preventDefault();
        var pruneVal = $("#prune-val").val();
        var cosineVal = $("#cosine-val").val();
        var searchVal = $(".form-control").val();

        if (pruneVal != "" && cosineVal != "") {
            $("#cosine-matrix").hide();
            $("#plot-refresh").show();

            $.ajax({

                "url" : "/refresh-text-analytics?tagname=" + searchVal + "&prune-val=" + pruneVal + "&cosine-val=" + cosineVal,
                "type" : "GET",

                error: function() {
                   $("#plot-refresh").hide();
                   $("#bad-tag-alert").fadeIn("slow").delay(2500).fadeOut("slow");
                },

                success: function(response) {
                    $("#plot-refresh").hide();
                    $("#cosine-matrix").show();

                    Highcharts.chart('cosine-matrix', {
                        chart: {
                            type: 'packedbubble',
                            height: '500px',

                        },
                        title: {
                            text: 'Question Title Semantic Similarity'
                        },
                        tooltip: {
                            useHTML: true,
                            pointFormat: '<b>{point.name}:</b> {point.y} tot. questions'
                        },
                        plotOptions: {
                            packedbubble: {
                                dataLabels: {
                                    enabled: true,
                                    format: '{point.name}',
                                    filter: {
                                        property: 'y',
                                        operator: '>',
                                        value: 250
                                    },
                                    style: {
                                        color: 'black',
                                        textOutline: 'none',
                                        fontWeight: 'normal'
                                    }
                                },
                                minPointSize: 5
                            }
                        },
                        series: response.cosineSimilarity,
                        responsive: {
                            rules: [{
                                condition: {
                                    maxWidth: 500
                                },
                                chartOptions: {
                                    legend: {
                                        align: 'right',
                                        verticalAlign: 'middle',
                                        layout: 'vertical'
                                    }
                                }
                            }]
                        }
                    });
                }
            })
        }
    });

});