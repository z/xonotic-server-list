$(document).ready(function () {

  function flatten(obj, includePrototype, into, prefix) {
    into = into || {};
    prefix = prefix || "";

    for (var k in obj) {
        if (includePrototype || obj.hasOwnProperty(k)) {
            var prop = obj[k];
            if (prop && typeof prop === "object" &&
                !(prop instanceof Date || prop instanceof RegExp)) {
                flatten(prop, includePrototype, into, prefix + k + "_");
            }
            else {
                into[prefix + k] = prop;
            }
        }
    }

    return into;
  }

  // Get the stats and filter them down.
  $.get('resources/data/stats.json', function(response) {

    var stats_data = response.data;

    var c3data = [];

    function newArray(element, index, array) {
      element.time = element.time * 1000;
      c3data.push(flatten(element));
    }

    stats_data.forEach(newArray);

    var chart = c3.generate({
      bindto: '#chart-players',
      data: {
        json: c3data,
        keys: {
          value: ['countries_CA', 'countries_UA', 'countries_US', 'countries_FR', 'countries_DE'],
          x: 'time'
        },
        types: {
            countries_CA: 'area-spline',
            countries_UA: 'area-spline',
            countries_US: 'area-spline',
            countries_FR: 'area-spline',
            countries_DE: 'area-spline'
        },
        groups: [['countries_CA', 'countries_UA', 'countries_US', 'countries_FR', 'countries_DE']]
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