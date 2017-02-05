var app = angular.module('app', []);

app.filter('pretty_lang', function() {
  return function(lang) {
    var media = lang.media.replace("_", " ");
    var name = lang.name;

    return  `[${media}] ${name}`
  }
});

app.controller('controller', ['$scope', '$http', function($scope, $http) {
    var languages_endpoint = '/api/v1/get_languages/';
    var app_endpoints = '/api/v1/get_apps/';

    $scope.langs_available = null;
    $scope.number_langs_selected = 0;
    $scope.lang_selected_ids = [];

    $scope.update_selected_counter = function(lang_selected_state){
        if(lang_selected_state === true){
            $scope.number_langs_selected += 1;
        }
        else if(lang_selected_state === false){
            $scope.number_langs_selected -= 1;
        }
        else{
            alert("Sorry, something went wrong: "+ lang_selected_state)
        }
    }

    $scope.get_games = function(){
        for(var i = 0; i < $scope.langs_available.length; i++){
            if($scope.langs_available[i].selected === true){
                $scope.lang_selected_ids.push($scope.langs_available[i].id)
            }
        }
        get_apps(app_endpoints, $scope.lang_selected_ids, 0, 25, $http, $scope);
    }


    get_available_languages(languages_endpoint, $http, $scope);

}]);

function get_available_languages(uri, http_client, scope){
    http_client({
  method: 'GET',
  url: uri
        }).then(function successCallback(response) {
            scope.langs_available= response.data;
            for(var i = 0; i < scope.langs_available.length; i++){
                scope.langs_available[i].selected = false;
            }

        }, function errorCallback(response) {
            alert("Sorry, something went wrong: " + response)
  });
}

function get_apps(app_endpoint, ids, start_index, end_index, http, scope){
      var uri = app_endpoint + `${ids.toString()}/${start_index}/${end_index}`

        http({
          method: 'GET',
          url: uri
                }).then(function successCallback(response) {
                scope.apps_available = response.data;

                }, function errorCallback(response) {
                    alert("Sorry, something went wrong: " + response)
          });
}
