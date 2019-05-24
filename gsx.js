var ws = new WebSocket('ws://beagle2.local:8080/');
    ws.onopen = function() {
        log("<span class='statusMsg' color='green'>connected</span>");
        console.log("onopen");
    };

    ws.onclose = function() {
        log("<span class='statusMsg'>NOT CONNECTED</span>");
        console.log("onclose");
    };

    ws.onmessage = function(event) {
        var f = JSON.parse(event.data);
	updateSpi1(f.spi1);
	updateSpi2(f.spi2);
        updateOLA(f.olad);
	updateCpu(f.cpu); 
    };