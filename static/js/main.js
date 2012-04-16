playAudio = function() {
	// var data = []; // just an array
	// for (var i=0; i<10000; i++) data[i] = Math.round(255 * Math.random()); // fill data with random samples
	// var wave = new RIFFWAVE(data); // create the wave file
	// var audio = new Audio(wave.dataURI); // create the HTML5 audio element
	// audio.play();

	var msg = {};
	msg["msg"] = "play";

	socket.send( JSON.stringify(msg));
}
sup = function() {
	playAudio();
}
createSocket = function() {
	socket = new WebSocket("ws://localhost:8888/audio");

	socket.onopen = function() { console.log("open..."); }
	socket.onclose = function() { console.log("closed."); }

	socket.onmessage = function(msg){  
    	var data = "data:audio/wav;base64,"+msg.data;
  		
		var audio = new Audio(data); // create the HTML5 audio element
		audio.addEventListener('ended', sup, false);
		audio.play();
	}
}

var socket;
$(document).ready( function() {
	$("#play").click( function( event ) {
		event.preventDefault();

		playAudio();
	});

	createSocket();
})