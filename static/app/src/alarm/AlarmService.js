(function(){
  'use strict';

  angular.module('alarm').factory('alarmService', function($resource) {
    return $resource('/api/v1/alarms/:id/',
      { id: '@id' },
      {
        update:{
          method: 'PUT'
        }
      },
      {
        stripTrailingSlashes: false
      }
    ); // need ' ' at the end: https://groups.google.com/d/msg/angular/taypgj_D3YQ/dUntRU5663sJ
  });

//  angular.module('alarm')
//         .service('alarmService', ['$q', '$resource', AlarmService]);

  /**
   * Alarms DataService
   * Uses embedded, hard-coded data model; acts asynchronously to simulate
   * remote data service call(s).
   *
   * @returns {{loadAll: Function}}
   * @constructor
   */
   /*
  function AlarmService($q, $resource){
    var alarms = [
      {
        alarm_hour: 7,
        alarm_min: 30,
        light_offset: 1200,
        name: "To early!!!",
        enabled: false
      },
      {
        alarm_hour: 11,
        alarm_min: 0,
        light_offset: 1800,
        name: null,
        enabled: true
      }
    ];

    // Promise-based API
    return {
      loadAllAlarms : function() {
        // Simulate async nature of real remote calls
        return $q.when(alarms);
      },
      addAlarm : function() {
      },
      updateAlarm : function() {

      }
    };
  }*/

})();
