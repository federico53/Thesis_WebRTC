
const IP = 'localhost';
const duration = 41000;

let peerConnection;

let remoteStream;

const ws = new WebSocket(`ws:${IP}:8080`);

if(peerConnection){
  peerConnection.close();
}
if(remoteStream){
  remoteStream.getTracks().forEach(track => track.stop());
}
peerConnection = new RTCPeerConnection()

let init = async () => {

    remoteStream = new MediaStream()

    document.getElementById('user-2').srcObject = remoteStream

    peerConnection.ontrack = (event) => {
        event.streams[0].getTracks().forEach((track) => {
        remoteStream.addTrack(track);
        });
    };
}

let createAnswer = async (offer) => {

    peerConnection.onicecandidate = async (event) => {

      if(event.candidate){
            console.log('Adding answer candidate...:', event.candidate)
        }
    };

    peerConnection.onicegatheringstatechange = () => {
        if(peerConnection.iceGatheringState === 'complete'){
            console.log('Stato raccolta ICE:', peerConnection.iceGatheringState);
            ws.send(JSON.stringify(peerConnection.localDescription));
        }
    };

    await peerConnection.setRemoteDescription(offer);

    let answer = await peerConnection.createAnswer();
    // const modifiedSDP = preferH264(answer.sdp);

    await peerConnection.setLocalDescription({type: answer.type, sdp: answer.sdp}); 


    // per la raccolta dati
    let statsInterval = setInterval(printStats, 1000);

    setTimeout(() => {
        clearInterval(statsInterval);
        downloadCsv();
    }, duration);
}


ws.onmessage = (event) => {
  
  let data;
  
  try{
    data = JSON.parse(event.data);
  } catch (error) {
    console.error('Errore di parsing JSON:', error);
    return;
  }
  
  if (data['type'] === 'offer'){
      init();
      createAnswer(data);
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

// Funzioni relative alla raccolta dati

let csv = '';
let index;

function reportToCsv(report, index) {
  const values = Object.values(report);
  if (typeof values[index] === 'string') {
    values[index] = values[index].replace(/,/g, ' ');
  }
  const csvRow = values.join(',');
  return `${csvRow}`;
}

async function printStats() {
  if (peerConnection) {
    const stats = await peerConnection.getStats();

    for (let report of stats.values()) {
      if (report.type === "inbound-rtp" && report.kind === "video") {
        if (!csv) {
          const keys = Object.keys(report);
          index = keys.indexOf('googTimingFrameInfo');
          csv = keys.join(',') + '\n';
        }
        csv += reportToCsv(report, index) + '\n';
      }
    }
  }
}

function downloadCsv() {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'receiver.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
