
const IP = '192.168.56.212';

let peerConnection;
let localStream;

const ws = new WebSocket(`ws:${IP}:8080`);

const localVideo = document.getElementById('user-1');
localVideo.src = `http://${IP}:8000/media/1.mp4`;

if(peerConnection){
    peerConnection.close();
}
if(localStream){
    localStream.getTracks().forEach(track => track.stop());
}

peerConnection = new RTCPeerConnection();

localVideo.addEventListener('canplay', () => {
    let stream; 
    const fps = 0;
    if(localVideo.captureStream){
        stream = localVideo.captureStream(fps);
    } else {
        console.error('Stream capture is not supported');
        stream = null;
    }
    localStream = stream;

    init();
})

let init = async () => {

    remoteStream = new MediaStream()

    localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream);
    });

}

let createOffer = async () => {

    console.log('Creazione offerta...');

    peerConnection.onicecandidate = async (event) => {

        if(event.candidate){
            console.log(JSON.stringify(peerConnection.localDescription));
        }
    };

    peerConnection.onicegatheringstatechange = () => {
        if(peerConnection.iceGatheringState === 'complete'){
            console.log('Stato raccolta ICE:', peerConnection.iceGatheringState);
            ws.send(JSON.stringify(peerConnection.localDescription));
        }
    };

    const offer = await peerConnection.createOffer();
    const modifiedSDP = preferH264(offer.sdp);

    await peerConnection.setLocalDescription({type: offer.type, sdp: modifiedSDP});
}

let addAnswer = async (answer) => {
    console.log('answer:', answer)
    if (!peerConnection.currentRemoteDescription){
        peerConnection.setRemoteDescription(answer);
    }

    // per la raccolta dati
    let statsInterval = setInterval(printStats, 1000);
    setTimeout(() => {
        clearInterval(statsInterval);
        downloadCsv();
    }, 41000);
}

ws.onmessage = (event) => {

    let data;
    
    try{
        data = JSON.parse(event.data);
    } catch (error) {
        console.error('Errore di parsing JSON:', error);
        return;
    }

    if (data['type'] === 'answer'){
        addAnswer(data);
    }
}

function preferH264(sdp) {
    let sdpLines = sdp.split('\r\n');
    let mLineIndex = sdpLines.findIndex(line => line.startsWith('m=video'));
    
    if (mLineIndex === -1) {
        return sdp;
    }

    // Trova l'indice del codec H.264 (98 è un esempio, potrebbe variare)
    let h264PayloadType = null;
    for (let i = mLineIndex + 1; i < sdpLines.length; i++) {
        if (sdpLines[i].startsWith('a=rtpmap')) {
            if (sdpLines[i].includes('H264/90000')) {
                h264PayloadType = sdpLines[i].split(' ')[0].split(':')[1];
                break;
            }
        }
    }

    if (h264PayloadType) {
        let mLine = sdpLines[mLineIndex];
        let elements = mLine.split(' ');
        let newMLine = [elements[0], elements[1], elements[2], h264PayloadType].concat(elements.slice(3).filter(pt => pt !== h264PayloadType));
        sdpLines[mLineIndex] = newMLine.join(' ');
    }

    return sdpLines.join('\r\n');
}

document.getElementById('connect').addEventListener('click', createOffer)

// Funzioni relative alla raccolta dati

let csv = '';

function reportToCsv(report) {
  const values = Object.values(report);
  const csvRow = values.join(',');
  return `${csvRow}`;
}

async function printStats() {
  if (peerConnection) {
    const stats = await peerConnection.getStats();

    for (let report of stats.values()) {
      // console.log("Report: ", report, "Type: ", report.type);
      if (report.type === "outbound-rtp" && report.kind === "video") {
        if (!csv) {
          const keys = Object.keys(report);
          csv = keys.join(',') + '\n';
        }
        csv += reportToCsv(report) + '\n';
      }
    }
  }
}

function downloadCsv() {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'sender.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
