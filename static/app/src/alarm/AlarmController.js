(function(){

  angular
       .module('alarm')
       .controller('AlarmController', [
          'alarmService', '$mdSidenav', '$mdBottomSheet', '$log', '$q', '$http',
          AlarmController
       ]);

  /**
   * Main Controller for the Angular Material Starter App
   * @param $scope
   * @param $mdSidenav
   * @param avatarsService
   * @constructor
   */
  function AlarmController( alarmService, $mdSidenav, $mdBottomSheet, $log, $q, $http) {
    var self = this;

    self.light_on = "AUTO";
    self.alarmService = alarmService;
    self.selected     = null;
    self.alarms       = [ ];
    self.selectAlarm  = selectAlarm;
    self.addAlarm     = addAlarm;
    self.removeAlarm  = removeAlarm;
    self.updateAlarm  = updateAlarm;
    self.toggleList   = toggleAlarmList;
    self.toggleLight  = toggleLight;
    self.getTimeString= getTimeString;
    self.showContactOptions  = showContactOptions;

    // Load all registered alarms
     var response = alarmService.query(function() {
       self.alarms   = [].concat(response);
       self.selected = self.alarms[0];
     });
     /*
    self.alarmService
          .loadAllAlarms()
          .then( function( alarms ) {
            self.alarms    = [].concat(alarms);
            self.selected = alarms[0];
          });
*/
    // *********************************
    // Internal methods
    // *********************************

    function getAlarms() {
     var response = alarmService.query(function() {
       self.alarms   = [].concat(response);
       self.selected = self.alarms[0];
     });
   }

   // Load all registered alarms
   getAlarms();

    /**
     * First hide the bottomsheet IF visible, then
     * hide or Show the 'left' sideNav area
     */
    function toggleAlarmList() {
      var pending = $mdBottomSheet.hide() || $q.when(true);

      pending.then(function(){
        $mdSidenav('left').toggle();
      });
    }

    /**
     * Select the current alarm
     * @param menuId
     */
    function selectAlarm ( alarm ) {
      self.selected = angular.isNumber(alarm) ? $scope.alarms[alarm] : alarm;
      self.toggleList();
    }

    /**
     * Addes an new alarm
     */
    function addAlarm () {
      console.log("addAlarm");
      var new_alarm = {"alarm_hour": 12, "alarm_min": 0, "light_offset": 60, "enabled": true, name: null};

    //  self.toggleList();
      self.alarmService.save(new_alarm, function(res) {
        new_alarm = res
        self.alarms.push(new_alarm);
        self.selected = new_alarm;
      });
    }

    /**
     * Updates an alarm
     * @param alarm
     */
    function updateAlarm (alarm) {
      console.log("updateAlarm");

      alarm.$update();
    }

    /**
    * removes an new alarm
    * @param alarm
    */
    function removeAlarm (alarm) {
     console.log("removeAlarm");
     self.alarmService.delete({id: alarm["id"]});
     getAlarms();
    }


    function toggleLight() {
      console.log("toggleLight");
      datat = {};
      if(self.light_on == "ON"){ // make off
        datat = {"brightness": 0.0, "duration": 3*60*60};
        self.light_on = "OFF";
      }else if( self.light_on == "OFF"){ // make alarm mode
        datat = {"brightness": 0.0, "duration": 0};
        self.light_on = "AUTO";
      }else{ // make on
        datat = {"brightness": 1.0, "duration": 3*60*60};
        self.light_on = "ON";
      }

      // Simple GET request example:
      $http({
        method: 'PUT',
        url: '/api/v1/light/',
        data: datat
      }).then(function successCallback(response) {
          // this callback will be called asynchronously
          // when the response is available
        }, function errorCallback(response) {
          // called asynchronously if an error occurs
          // or server returns response with an error status.
        });
    }


    function getTimeString(alarm){
      var h = alarm["alarm_hour"];
      var m = alarm["alarm_min"];
      var s = "" + (h<10?"0":"") + h + ":";
      s += (m<10?"0":"") + m;
      return s;
    }

    /**
     * Show the bottom sheet
     */
    function showContactOptions($event) {
    }

  }

})();
