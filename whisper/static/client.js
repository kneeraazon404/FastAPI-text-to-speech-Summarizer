// peer connection
var pc = null;
var dc = null, dcInterval = null;

transcriptionOutput = document.getElementById('output');
start_btn = document.getElementById('start');
stop_btn = document.getElementById('stop');
statusField = document.getElementById('status');


var lastTrans = document.createElement('span');
lastTrans.innerText = '💤';
lastTrans.classList.add('partial');
transcriptionOutput.appendChild(lastTrans);
var imcompleteTrans = '';
//var kaldiServerUrl = 'https://18.132.134.208';
var kaldiServerUrl = 'http://localhost:8888';

enableDownloadButton(false);

let bufferSize = 2048,
	AudioContext,
	context,
	processor,
	input,
	globalStream;

var socket;
//vars
let streamStreaming = false;

function btn_show_stop() {
    start_btn.classList.add('d-none');
    stop_btn.classList.remove('d-none');
}

function btn_show_start() {
    stop_btn.classList.add('d-none');
    start_btn.classList.remove('d-none');
    lastTrans.innerText = '💤';
    statusField.innerText = 'Press start';
}


function negotiate() {
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }

                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        console.log(offer.sdp);
        return fetch(kaldiServerUrl + '/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        console.log(answer.sdp);
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        console.log(e);
        btn_show_start();
    });
}

function start() {
    btn_show_stop();
    enableDownloadButton(false);

    lastTrans.innerText = '💤';
    statusField.innerText = 'Connecting...';

//    websocket = new WebSocket("http://127.0.0.1:8888/ws");
    socket = io.connect(kaldiServerUrl);

    socket.on('disconnect', function()
    {
//        clearInterval(dcInterval);
        console.log('Closed data channel');
        stop();
    });

    socket.on('connect', function () {
        console.log('Opened data channel');
        var constraints = {
            audio: true,
            video: false,
        };

        streamStreaming = true;
        AudioContext = window.AudioContext || window.webkitAudioContext;
        context = new AudioContext({
            // if Non-interactive, use 'playback' or 'balanced' // https://developer.mozilla.org/en-US/docs/Web/API/AudioContextLatencyCategory
            latencyHint: 'interactive',
        });

        processor = context.createScriptProcessor(bufferSize, 1, 1);
        processor.connect(context.destination);
        context.resume();

        var microphoneProcess = function (e) {
            var left = e.inputBuffer.getChannelData(0);
            // var left16 = convertFloat32ToInt16(left); // old 32 to 16 function
            var left16 = downsampleBuffer(left, 44100, 16000)
            socket.send(left16);
        }


        navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
            globalStream = stream;
            input = context.createMediaStreamSource(stream);
            input.connect(processor);

            processor.onaudioprocess = function (e) {
                microphoneProcess(e);
            };
        }, function (err) {
            console.log('Could not acquire media: ' + err);
            btn_show_start();
        });
    });

    socket.on('message', function (data) {
        statusField.innerText = 'Listening...';
        console.log(data);
        var msg = JSON.parse(data);
/*
        if (msg.endsWith('\n')) {
            lastTrans.innerText = imcompleteTrans + msg.substring(0, msg.length - 1);
            lastTrans.classList.remove('partial');
            lastTrans = document.createElement('span');
            lastTrans.classList.add('partial');
            lastTrans.innerText = '...';
            transcriptionOutput.appendChild(lastTrans);

            imcompleteTrans = '';
        } else if (msg.endsWith('\r')) {
            lastTrans.innerText = imcompleteTrans + msg.substring(0, msg.length - 1) + '...';
            imcompleteTrans = '';
        } else {
            imcompleteTrans += msg;
        }
*/
        if (msg.text) {
                lastTrans.innerText = msg.text;
                lastTrans.classList.remove('partial');
                lastTrans = document.createElement('span');
                lastTrans.classList.add('partial');
                lastTrans.innerText = '...';
                transcriptionOutput.appendChild(lastTrans);
        } else if (msg.partial) {
                lastTrans.innerText = msg.partial;
        } else {
                console.log("oh");
        }
    });
}


function stop() {
    // close data channel
    if (socket) {
        socket.close();
    }

    streamStreaming = false;
    let track = globalStream.getTracks()[0];
	track.stop();
	input.disconnect(processor);
	processor.disconnect(context.destination);
	context.close().then(function () {
		input = null;
		processor = null;
		context = null;
		AudioContext = null;
	});

	socket = null;

    // close peer connection
    setTimeout(function () {
    	enableDownloadButton(true);
    }, 500);

    btn_show_start();
}

var downsampleBuffer = function (buffer, sampleRate, outSampleRate) {
	if (outSampleRate == sampleRate) {
		return buffer;
	}
	if (outSampleRate > sampleRate) {
		throw "downsampling rate show be smaller than original sample rate";
	}
	var sampleRateRatio = sampleRate / outSampleRate;
	var newLength = Math.round(buffer.length / sampleRateRatio);
	var result = new Int16Array(newLength);
	var offsetResult = 0;
	var offsetBuffer = 0;
	while (offsetResult < result.length) {
		var nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
		var accum = 0, count = 0;
		for (var i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
			accum += buffer[i];
			count++;
		}

		result[offsetResult] = Math.min(1, accum / count) * 0x7FFF;
		offsetResult++;
		offsetBuffer = nextOffsetBuffer;
	}
	return result.buffer;
}

function enableDownloadButton(enable) {
	$("#download").attr("disabled", !enable);
}

function download()
{
	$.get(kaldiServerUrl + "/wav_path", function(data) {
		console.log(data);
		$("#download_href").attr("href", kaldiServerUrl + "/"+data).attr("download",kaldiServerUrl + "/"+data);
		$("#download_href")[0].click();
	})
}

