document.onload = () => {
    setTheme('auto')
}

const promptField = document.getElementById('prompt-field')
const imageField = document.getElementById('image-field')
const recognizeButton = document.getElementById('recognize-button')
const videoPreview = document.getElementById('video-preview')
const camera = document.getElementById('camera')
const canvasElement = document.getElementById('canvas')

let mediaStreamTrack = null

function showCamera() {
    camera.style.display = "flex"
    navigator.mediaDevices.getUserMedia({
        video: {
            facingMode: "environment"
        },
        audio: false
    }).then(stream => {
        mediaStreamTrack = stream
        videoPreview.srcObject = stream
        videoPreview.muted = true
        videoPreview.play();
    })
}

function takePhoto() {
    canvasElement.width = videoPreview.videoWidth;
    canvasElement.height = videoPreview.videoHeight;
    const canvasContext = canvasElement.getContext('2d');
    canvasContext.drawImage(videoPreview, 0, 0, videoPreview.videoWidth, videoPreview.videoHeight);
    const img = canvasElement.toDataURL('image/png');
    imageField.setAttribute("base64", img.split(",")[1])
    mediaStreamTrack.getVideoTracks().forEach(track => {
        track.stop()
    })
    videoPreview.srcObject = null
    camera.style.display = "none"
}

function startRecognize() {
    recognition = new webkitSpeechRecognition() || new SpeechRecognition();
    recognition.interimResults = true

    recognition.onresult = (e) => {
        document.querySelector('#send-button').removeAttribute('disabled')
        promptField.value = e.results[0][0].transcript
    }

    recognition.onend = (e) => {
        recognizeButton.innerHTML = `<span class="material-symbols-outlined">mic</span>`
    }

    recognition.onnomatch = (e) => {
        mdui.snackbar({
            message: "No results found"
        })
    }

    recognition.start()
    recognizeButton.innerHTML = `<mdui-circular-progress></mdui-circular-progress>`
}

function send() {
    const message = promptField.value
    const image = imageField.getAttribute("base64")
    let step = 0
    promptField.value = ""
    promptField.setAttribute("disabled", "disabled")
    imageField.setAttribute("base64", "Undefined")
    document.querySelector('#send-button').setAttribute('disabled', 'disabled')
    mdui.$("#chat").append(`<question-message text="${message}" image="${image}"></question-message>`)
    fetch("/chat", {
        method: "POST", body: JSON.stringify({
            "message": message, "image": image
        })
    }).then(response => {
        const reader = response.body.getReader();
        return reader.read().then(function process({done, value}) {
            if (done) {
                promptField.removeAttribute("disabled")
                return;
            }
            var data = new TextDecoder().decode(value)
            data.split("-|BOWERY SPLIT|-").forEach((content) => {
                var cont = content.trim()
                if (cont.startsWith("{")) {
                    data = JSON.parse(cont)
                    if (data.type === "text") {
                        if (step === 0) {
                            mdui.$("#chat").append(`<answer-message text="${data.message}" image="Undefined"></answer-message>`)
                            step = 1
                        } else {
                            mdui.$("#chat answer-message:last-child").attr("text", mdui.$("#chat answer-message:last-child").attr("text") + data.message)
                        }

                    } else if (data.type === "image") {
                        if (step === 0) {
                            mdui.$("#chat").append(`<answer-message text="" image="${data.message}"></answer-message>`)
                            step = 1
                        } else {
                            mdui.$("#chat answer-message:last-child").attr("image", data.message)
                        }
                    }

                }
            })
            return reader.read().then(process);
        });
    })
}

function speakNow(content) {
    const synth = window.speechSynthesis
    const msg = new SpeechSynthesisUtterance()
    msg.text = content.replace(/\p{Emoji_Presentation}/gu, '')
    synth.speak(msg)
}