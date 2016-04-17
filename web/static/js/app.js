$(document).ready(function () {

  function flatten(obj, includePrototype, into, prefix) {
    into = into || {};
    prefix = prefix || "";

    for (var k in obj) {
      if (includePrototype || obj.hasOwnProperty(k)) {
        var prop = obj[k];
        if (prop && typeof prop === "object" && !(prop instanceof Date || prop instanceof RegExp)) {
          flatten(prop, includePrototype, into, prefix + k + "_");
        }
        else {
          into[prefix + k] = prop;
        }
      }
    }

    return into;
  }

  // Handle tabs on page reload
  function handleTabs() {
    // Javascript to enable link to tab
    var url = document.location.toString();
    if (url.match('#')) {
      $('.navbar-tabs a[href=#' + url.split('#')[1] + ']').tab('show');
    }

    // Change hash for page-reload
    $('.navbar-tabs a').on('shown.bs.tab', function (e) {
      history.pushState(null, null, $(this).attr('href'));
      window.location.hash = e.target.hash;
    });
  }

  handleTabs();
  var p = new Ping();

  var table = $('#table-serverlist').DataTable({
    ajax: GLOBAL.api_url + '/server_list',
    lengthMenu: [25, 50, 100, 250],
    pageLength: 50,
    order: [[4, 'desc']],
    fixedHeader: {
      header: true,
      headerOffset: $('#main-nav').height()
    },
    processing: true,
    deferRender: true,
    language: {
      search: "",
      lengthMenu: '_MENU_'
    },
    dom: "<'#table-controls'lf>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row footer-bar navbar-inverse'<'col-sm-5 navbar-brand'i><'col-sm-7'p>>",
    columns: [
      {
        data: 'country'
      },
      {
        data: 'country'
      },
      {
        data: 'name'
      },
      {
        data: 'address'
      },
      { // players
        data: function (row, type, val, meta) {
          return {
            'total_players': row.total_players,
            'max_players': row.max_players
          };
        }
      },
      {
        data: 'modname'
      },
      {
        data: 'map'
      },
      {
        data: 'gametype'
      },
      {
        data: 'version'
      },      
      {
        defaultContent: 'unknown'
      }
    ],
    columnDefs: [
      { // country
        targets: 0,
        orderData: 1,
        render: function (data, type, full, meta) {
          var cc = data.toLowerCase();
          return '<span class="flag-icon flag-icon-' + cc + '" title="' + cc + '"></span>';
        }
      },
      { // country (lookup)
        targets: 1,
        visible: false,
        searchable: false
      },
      { // players
        targets: 4,
        type: 'natural',
        render: function (data, type, full, meta) {
          return data.total_players + '/' + data.max_players;
        }
      },
      { // ping
        targets: 9,
        render: function (data, type, full, meta) {
          return data;
        }
      }
    ],
    initComplete: function (settings, json) {

      // Make the search more better ;)
      $('#table-serverlist_filter')
        .addClass('pull-right')
        .css('position', 'relative')
        .append('<span id="search-clear" class="fa fa-times-circle-o hidden"></span>');

      $('#search-clear').click(function (e) {
        $('#table-serverlist_filter input').val('');
        table.search('').draw();
      });

      // Put the controls in the navbar
      $('#table-controls').detach().appendTo('#nav-table-controls');

      // Style and show
      $('#table-serverlist_length').addClass('pull-right');
      $('#table-controls .btn').addClass('btn-sm');
      $('#table-controls .dt-buttons').addClass('pull-right');
      $('#table-controls').show();

      var searchTerm = $('#table-serverlist_filter input').val();
      if (searchTerm) {
        $('#search-clear').removeClass('hidden');
      }

    },
    drawCallback: function (settings) {
      $('#table-controls').show();

      setTimeout(function() {
        refreshPings();
      }, 1000);
    }
  });


  function refreshPings() {
    var tableApi = $('#table-serverlist').DataTable();

    var addresses = tableApi
      .columns(3)
      .data()
      .eq(0)
      .sort();

    var ips = [];
    $.each(addresses, function(index, data) {
      ips.push(data.split(':')[0]);
    });

    var ipsFiltered = ips.filter(function(item, i, ar){ return ar.indexOf(item) === i; });

    var i = 0;

    function pingServer(ipsFiltered) {

      var ip = ipsFiltered.pop();

      if (i < 150) {

        p.ping('http://' + ip, function (ping) {

          var dd = tableApi
            .rows()
            .eq(0)
            .each(function(index) {
              i++;
              var row = tableApi.row( index );

              if ( row.data().address.indexOf(ip) > -1 ) {
                tableApi.cell( index, 9 ).data(ping);
              }

              //setTimeout(pingServer(ipsFiltered), 2000);
              pingServer(ipsFiltered);

            });

        }, 5000);

      }

    }

    pingServer(ipsFiltered);

  }

  // Get the stats and filter them down.
  $.get(GLOBAL.api_url + '/player_stats/', function (response) {

    var stats_data = response.data;

    // Need to do this until: https://github.com/masayuki0812/c3/issues/1471
    var acc = 0;
    function flattenCountries(element, index, array) {
      var p1 = element.total_players;
      acc += p1;
      var moving_average = acc / (index + 1);
      element.time = element.time * 1000;
      element.moving_average = moving_average.toFixed(2);
      c3data.push(flatten(element));
      $.each(element.countries, function(index, value) {
        allCountries.push('countries_' + index);
      });
    }

    var c3data = [];
    var allCountries = [];
    stats_data.forEach(flattenCountries);

    var countryList = allCountries.filter(function(item, i, ar){ return ar.indexOf(item) === i; });

    var countryTypes = {};
    for (var i = 0; i < countryList.length; i++) {
      countryTypes[countryList[i]] = 'area-spline';
    }

    countryTypes['total_players'] = 'line';
    countryTypes['moving_average'] = 'line';

    var countryNames = {};
    for (var i = 0; i < countryList.length; i++) {
      countryNames[countryList[i]] = countryList[i].replace('countries_', '');
    }

    countryNames['total_players'] = 'Total Players';
    countryNames['moving_average'] = 'Moving Average';

    var xKeys = countryList.slice().sort();
    xKeys.push('total_players');
    xKeys.push('moving_average');

    var chart = c3.generate({
      bindto: '#chart-players',
      data: {
        order: null,
        json: c3data,
        keys: {
          value: xKeys,
          x: 'time'
        },
        names: countryNames,
        colors: {
          countries_CA: '#9e0142',
          countries_CL: '#d53e4f',
          countries_DE: '#f46d43',
          countries_FR: '#fdae61',
          countries_GB: '#fee08b',
          countries_NL: '#ffffbf',
          countries_RU: '#e6f598',
          countries_UA: '#abdda4',
          countries_US: '#66c2a5',
          countries_ZA: '#3288bd',
          countries_ES: '#5e4fa2',
          total_players: '#0000cc',
          moving_average: '#cc0000'
        },
        types: countryTypes,
        groups: [countryList]
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: {
            // waiting on this https://github.com/masayuki0812/c3/pull/1400
            culling: true,
            max: 15,
            //format: '%Y-%m-%d %H:%M',
            format: '%I:%M%p'
          }
        }
      },
      subchart: {
        show: true
      },
      zoom: {
        enabled: true
      },
      point: {
        show: false
      },
      onrendered: function () {
        // Mostly c3 hacks
        if ($('#stacked-on').hasClass('active')) {
          $('.c3-shapes.c3-areas .c3-shape').css('opacity', 0.7);
        } else {
          $('.c3-shapes.c3-areas .c3-shape').css('opacity', 0.4);
        }
      }
    });

    $('#stacked-off').click(function() {
      chart.groups([[]]);
      $(this).addClass('active');
      setTimeout(function() {
        $('.c3-shapes.c3-areas .c3-shape').animate({'opacity': 0.4}, 200);
      }, 450);
      $('#stacked-on').removeClass('active');
    });

    $('#stacked-on').click(function() {
      chart.groups([countryList]);
      $(this).addClass('active');
      setTimeout(function() {
        $('.c3-shapes.c3-areas .c3-shape').animate({'opacity': 0.7}, 200);
      }, 450);
      $('#stacked-off').removeClass('active');
    });

    $('#stacked-on').click();

  });

  // Need to hide datatables when changing tabs for fixedHeader
  var visible = true;
  var tableContainer = $(table.table().container());

  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {

    var currentTab = $('.nav li.active a').attr('href');

    switch (currentTab) {

      case "#serverlist":

        visible = false;

        break;

      case "#statistics":

      case "#about":

      default:

        visible = false;

    }

    $('#nav-table-controls').hide();

    table.fixedHeader.adjust();

    // decide whether to show the table or not
    if (visible) { // hide table
      tableContainer.css('display', 'none');
    } else { // show table
      tableContainer.css('display', 'block');
    }

  });

  $('[href=#serverlist]').click(function() {
    setTimeout(function() {
      $('#nav-table-controls').show();
    }, 10);
  });

});
