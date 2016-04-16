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
  $.get('resources/data/stats.json', function (response) {

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
    }

    var c3data = [];
    stats_data.forEach(flattenCountries);

    var countryList = [
      'countries_CA',
      'countries_UA',
      'countries_US',
      'countries_FR',
      'countries_DE',
      'countries_AU',
      'countries_RU',
      'countries_GB',
      'countries_ZA',
      'countries_NL',
      'countries_CL'
    ];

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
      point: {
        show: false
      }
    });

  });

});