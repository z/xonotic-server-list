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

  // Get the stats and filter them down.
  $.get('http://127.0.0.1:8000/player_stats/', function (response) {

    var stats_data = response.data;

    // Need to do this until: https://github.com/masayuki0812/c3/issues/1471
    var acc = 0;
    function flattenCountries(element, index, array) {
      var p1 = element.total_players;
      acc += p1;
      var moving_average = acc / (index + 1);
      element.time = element.time * 1000;
      element.moving_average = moving_average;
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

    var xKeys = countryList.slice();
    xKeys.push('total_players');
    xKeys.push('moving_average');

    var chart = c3.generate({
      bindto: '#chart-players',
      data: {
        json: c3data,
        keys: {
          value: xKeys,
          x: 'time'
        },
        colors: {
          countries_CA: '#9e0142',
          countries_UA: '#d53e4f',
          countries_US: '#f46d43',
          countries_FR: '#fdae61',
          countries_DE: '#fee08b',
          countries_AU: '#ffffbf',
          countries_RU: '#e6f598',
          countries_GB: '#abdda4',
          countries_ZA: '#66c2a5',
          countries_NL: '#3288bd',
          countries_CL: '#5e4fa2',
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
            format: '%Y-%m-%d %H:%M'
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
      }
    });

    $('#stacked-off').click(function() {
      chart.groups([[]]);
      $(this).addClass('active');
      setTimeout(function() {
        $('.c3-shapes.c3-areas .c3-shape').css('opacity', 0.4);
      }, 100);
      $('#stacked-on').removeClass('active');
    });

    $('#stacked-on').click(function() {
      chart.groups([countryList]);
      $(this).addClass('active');
      setTimeout(function() {
        $('.c3-shapes.c3-areas .c3-shape').css('opacity', 0.7)
      }, 100);
      $('#stacked-off').removeClass('active');
    });

  });

});