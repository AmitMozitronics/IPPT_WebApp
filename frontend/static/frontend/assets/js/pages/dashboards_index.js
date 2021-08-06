$(function() {
  new PerfectScrollbar(document.getElementById("tasks-inner"));
  new PerfectScrollbar(document.getElementById("tab-table-1"));
  new PerfectScrollbar(document.getElementById("tab-table-2"));
});
// $(document).ready(pipeChartBuilderAjax);
function pipeChartBuilderAjax(pipe_data) {
  setTimeout(function() {
    // Bar Chart
    // console.log(pipe_data);
    $(function() {
      am4core.useTheme(am4themes_animated);
      var chart = am4core.create("statistics-chart-1", am4charts.XYChart);

      // Add data
      // console.log(pipe_data);
      chart.data = [];
      //   for(i = 0; i < 400; i ++)
      //   chart.data.push(
      //     {
      //     //   period: formatUTCDateString(new Date(d.site_time).toUTCString()),
      //     period: String(i),
      //       Weight: i
      //     }
      // );
      for (i = pipe_data.data.length - 1; i >= 0; i--) {
        chart.data.push({
          period: formatUTCTimeString(new Date(pipe_data.data[i].site_time).toUTCString()),
          Weight: pipe_data.data[i].weight
        });
      }
      //    {
      //     period: '8:31:42 PM',
      //     //demo1: 0,
      //     Weight: 60
      // }, {
      //     period: '8:38:42 PM',
      //     //demo1: 50,
      //     Weight: 5
      // }, {
      //     period: '8:39:42 PM',
      //     //demo1: 20,
      //     Weight: 100
      // }, {
      //     period: '8:45:42 PM',
      //     //demo1: 60,
      //     Weight: 60
      // },
      // {
      //     period: '8:55:42 PM',
      //     //demo1: 20,
      //     Weight: 170
      // },
      //  {
      //     period: '8:58:42 PM',
      //     //demo1: 60,
      //     Weight: 25
      // }, {
      //     period: '8:59:42 PM',
      //     //demo1: 10,
      //     Weight: 60
      // }
      //];

      // Create axes
      var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
      categoryAxis.dataFields.category = "period";

      // First value axis
      var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

      // First series
      var series = chart.series.push(new am4charts.LineSeries());
      series.dataFields.valueY = "demo1";
      series.dataFields.categoryX = "period";
      series.name = "demo1";
      series.tooltipText = "{name}: [bold]{valueY}[/]";
      series.strokeWidth = 4;
      series.strokeDasharray = 10;
      series.tensionY = 1;
      series.tensionX = 0.8;
      series.fill = am4core.color("#C4C2C3");
      series.stroke = am4core.color("#C4C2C3");

      // Second series
      var series2 = chart.series.push(new am4charts.LineSeries());
      series2.dataFields.valueY = "Weight";
      series2.dataFields.categoryX = "period";
      series2.name = "Weight";
      series2.tooltipText = "{name}: [bold]{valueY}[/]";
      series2.strokeWidth = 4;
      series2.tensionY = 1;
      series2.tensionX = 0.8;
      series2.fill = am4core.color("#716aca");
      series2.stroke = am4core.color("#716aca");
      var dropShadow = new am4core.DropShadowFilter();
      dropShadow.dy = 15;
      dropShadow.dx = 1;
      dropShadow.blur = 8;
      dropShadow.opacity = 0.5;
      dropShadow.color = "#716aca";
      series2.filters.push(dropShadow);

      // Add cursor
      chart.cursor = new am4charts.XYCursor();
      categoryAxis.renderer.grid.template.strokeOpacity = 0;
    });
  }, 400);
  buildchart();
  $(window).on("resize", function() {
    buildchart();
  });
  $("#mobile-collapse").on("click", function() {
    setTimeout(function() {
      buildchart();
    }, 700);
  });
}

function buildchart() {
  $(function() {
    //Flot Base Build Option for bottom join
    var options_bt = {
      legend: {
        show: false
      },
      series: {
        label: "",
        shadowSize: 0,
        curvedLines: {
          active: true,
          nrSplinePoints: 20
        }
      },
      tooltip: {
        show: true,
        content: "x : %x | y : %y"
      },
      grid: {
        hoverable: true,
        borderWidth: 0,
        labelMargin: 0,
        axisMargin: 0,
        minBorderMargin: 0,
        margin: {
          top: 5,
          left: 0,
          bottom: 0,
          right: 0
        }
      },
      yaxis: {
        min: 0,
        max: 30,
        color: "transparent",
        font: {
          size: 0
        }
      },
      xaxis: {
        color: "transparent",
        font: {
          size: 0
        }
      }
    };

    //Flot Base Build Option for Center card
    var options_ct = {
      legend: {
        show: false
      },
      series: {
        label: "",
        shadowSize: 0,
        curvedLines: {
          active: true,
          nrSplinePoints: 20
        }
      },
      tooltip: {
        show: true,
        content: "x : %x | y : %y"
      },
      grid: {
        hoverable: true,
        borderWidth: 0,
        labelMargin: 0,
        axisMargin: 0,
        minBorderMargin: 5,
        margin: {
          top: 8,
          left: 8,
          bottom: 8,
          right: 8
        }
      },
      yaxis: {
        min: 0,
        max: 30,
        color: "transparent",
        font: {
          size: 0
        }
      },
      xaxis: {
        color: "transparent",
        font: {
          size: 0
        }
      }
    };
    //Flot Order Chart Start
    $.plot(
      $("#order-chart-1"),
      [
        {
          data: [
            [0, 30],
            [1, 5],
            [2, 26],
            [3, 10],
            [4, 22],
            [5, 30],
            [6, 5],
            [7, 26],
            [8, 10]
          ],
          color: "#fff",
          lines: {
            show: true,
            fill: false,
            lineWidth: 3
          },
          points: {
            show: true,
            radius: 4,
            fillColor: "#fff",
            fill: true
          },
          curvedLines: {
            apply: false
          }
        }
      ],
      options_ct
    );
    $.plot(
      $("#ecom-chart-3"),
      [
        {
          data: [
            [0, 30],
            [1, 5],
            [2, 26],
            [3, 10],
            [4, 22],
            [5, 30],
            [6, 5],
            [7, 26],
            [8, 10]
          ],
          color: "#716aca",
          lines: {
            show: true,
            fill: false,
            lineWidth: 3
          },
          points: {
            show: true,
            radius: 4,
            fillColor: "#fff",
            fill: true
          },
          curvedLines: {
            apply: false
          }
        }
      ],
      options_ct
    );
  });
}
