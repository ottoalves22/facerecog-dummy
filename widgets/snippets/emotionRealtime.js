<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@2.4.0/dist/tf.min.js"></script>
<script
    src="https://cdn.jsdelivr.net/npm/@tensorflow-models/face-landmarks-detection@0.0.1/dist/face-landmarks-detection.js">
</script>

<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@2.4.0/dist/tf.min.js"></script>
<script
    src="https://cdn.jsdelivr.net/npm/@tensorflow-models/face-landmarks-detection@0.0.1/dist/face-landmarks-detection.js"></script>

<script>
            const token = '<ACCESS_TOKEN>'; // adicione aqui o seu token de aplicação
    
            /* Principais elementos da interface:
                - faceRecognition: <div> que engloba o componente
                - camera: <video> que exibe a captura da webcam
                - photoTaken: <canvas> que exibe a foto capturada
    
                - btnEnableCamera: <button> que habilita a captura da webcam
            */
            let faceEmotion = document.getElementById('face-emotion')
    
            let faceRecognition = document.getElementById('photo-camera')
            let camera = faceRecognition.querySelector('video');
            let photoTaken = faceRecognition.querySelector('canvas');
    
            let btnEnableCamera = document.getElementById('enable-camera');
    
            /* Elementos que exibem a predição de emoção na interface */
            let emotionSurprise = document.getElementById('emotion-suprise');
            let emotionHappy = document.getElementById('emotion-happy');
            let emotionNeutral = document.getElementById('emotion-neutral');
            let emotionDisgust = document.getElementById('emotion-disgust');
            let emotionSad = document.getElementById('emotion-sad');
            let emotionAngry = document.getElementById('emotion-angry');
            let emotionFear = document.getElementById('emotion-fear');
            let emotionStatus = document.getElementById('emotion-status');
    
            let emotionSurpriseProgress = emotionSurprise.querySelector(".progress");
            let emotionHappyProgress = emotionHappy.querySelector(".progress");
            let emotionNeutralProgress = emotionNeutral.querySelector(".progress");
            let emotionDisgustProgress = emotionDisgust.querySelector(".progress");
            let emotionSadProgress = emotionSad.querySelector(".progress");
            let emotionAngryProgress = emotionAngry.querySelector(".progress");
            let emotionFearProgress = emotionFear.querySelector(".progress");
    
            let emotionSurpriseResult = emotionSurprise.querySelector(".result");
            let emotionHappyResult = emotionHappy.querySelector(".result");
            let emotionNeutralResult = emotionNeutral.querySelector(".result");
            let emotionDisgustResult = emotionDisgust.querySelector(".result");
            let emotionSadResult = emotionSad.querySelector(".result");
            let emotionAngryResult = emotionAngry.querySelector(".result");
            let emotionFearResult = emotionFear.querySelector(".result");
    
            /* Variáveis complementares da detecção de emoções */
            let emotions = []; //["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"];
            let emotionModel = null;
    
            let output = null;
            let model = null;
    
    
            /*  
                function startWebcam(videoElement)
                - Inicializa a captura da câmera, pedindo permissão para acesso à câmera. Caso a permissão for negada, exibe-se uma mensagem de erro.
                - Carrega o modelo treinado para reconhecimento de emoções.
                
                Parâmetros:
                - videoElement (obrigatório): elemento <video> no qual será exibido a captura da câmera.
                
                Retorno da função: Nenhum retorno
            */
            function startWebcam(videoElement) {
                navigator.mediaDevices.getUserMedia({
                    video: true
                }).then((stream) => {
                    window.localStream = stream;
                    videoElement.srcObject = stream;
                    videoElement.play();
    
                    (async () => {
                        model = await faceLandmarksDetection.load(
                            faceLandmarksDetection.SupportedPackages.mediapipeFacemesh
                        );
    
                        let canvas = document.getElementById("output");
                        canvas.width = videoElement.width;
                        canvas.height = videoElement.height;
    
                        //Constrói um espelho da câmera
                        output = canvas.getContext("2d");
                        output.translate(canvas.width, 0);
                        output.scale(-1, 1);
    
                        //Carregar o modelo
                        emotionModel = await tf.loadLayersModel('model/facemo.json');
                        trackFace();
                    })();
    
                    btnEnableCamera.classList.add('hidden');
                }).catch(() => {
                    btnEnableCamera.classList.remove('hidden');
                    alert('Não foi possível acessar a câmera');
                }).finally(() => {
                    camera.classList.remove('hidden');
                })
            }
    
    
            /*  
                async function predictEmotion(points)
                - Função assíncrona que realiza a predição de emoção com o tensorFlow JS
                
                Parâmetros:
                - points (obrigatório): Pontos relacionados a posição do nariz, bochechas, olhos, sobrancelhas e boca
                
                Retorno da função: Array com a predição de emoção.
            */
            async function predictEmotion(points) {
                let result = tf.tidy(() => {
                    const xs = tf.stack([tf.tensor1d(points)]);
                    return emotionModel.predict(xs);
                });
                let prediction = await result.data();
                result.dispose();
                return prediction;
            }
    
    
            /*  
                async function trackFace()
                - Função assíncrona que realiza a predição de emoção com o tensorFlow JS
                
                Parâmetros:
                - points (obrigatório): Pontos relacionados a posição do nariz, bochechas, olhos, sobrancelhas e boca
                
                Retorno da função: Array com a predição de emoção.
            */
            async function trackFace() {
                const faces = await model.estimateFaces({
                    input: camera,
                    returnTensors: false,
                    flipHorizontal: false,
                });
                output.drawImage(
                    camera,
                    0, 0, camera.width, camera.height,
                    0, 0, camera.width, camera.height
                );
    
                let points = null;
                faces.forEach(face => {
                    //Bounding box dos rostos
                    const x1 = face.boundingBox.topLeft[0];
                    const y1 = face.boundingBox.topLeft[1];
                    const x2 = face.boundingBox.bottomRight[0];
                    const y2 = face.boundingBox.bottomRight[1];
                    const bWidth = x2 - x1;
                    const bHeight = y2 - y1;
    
                    //Capturar nariz, bochechas, olhos, sobrancelhas e boca
                    const features = [
                        "noseTip",
                        "leftCheek",
                        "rightCheek",
                        "leftEyeLower1", "leftEyeUpper1",
                        "rightEyeLower1", "rightEyeUpper1",
                        "leftEyebrowLower",
                        "rightEyebrowLower",
                        "lipsLowerInner",
                        "lipsUpperInner",
                    ];
                    points = [];
                    features.forEach(feature => {
                        face.annotations[feature].forEach(x => {
                            points.push((x[0] - x1) / bWidth);
                            points.push((x[1] - y1) / bHeight);
                        });
                    });
                });
    
                //Se encontrar um rosto, executar a predição de emoção
                if (points) {
                    let emotion = await predictEmotion(points);
                    emotions = emotion;
                    emotionSurpriseProgress.style = "width:" + Math.round(emotion[6] * 100) + "%";
                    emotionSurpriseResult.innerHTML = Math.round(emotion[6] * 100) + "%";
    
                    emotionHappyProgress.style = "width:" + Math.round(emotion[3] * 100) + "%";
                    emotionHappyResult.innerHTML = Math.round(emotion[3] * 100) + "%";
    
                    emotionNeutralProgress.style = "width:" + Math.round(emotion[4] * 100) + "%";
                    emotionNeutralResult.innerHTML = Math.round(emotion[4] * 100) + "%";
    
                    emotionDisgustProgress.style = "width:" + Math.round(emotion[1] * 100) + "%";
                    emotionDisgustResult.innerHTML = Math.round(emotion[1] * 100) + "%";
    
                    emotionSadProgress.style = "width:" + Math.round(emotion[5] * 100) + "%";
                    emotionSadResult.innerHTML = Math.round(emotion[5] * 100) + "%";
    
                    emotionAngryProgress.style = "width:" + Math.round(emotion[0] * 100) + "%";
                    emotionAngryResult.innerHTML = Math.round(emotion[0] * 100) + "%";
    
                    emotionFearProgress.style = "width:" + Math.round(emotion[2] * 100) + "%";
                    emotionFearResult.innerHTML = Math.round(emotion[2] * 100) + "%";
    
                    emotionStatus.innerHTML = "Atualizado a cada 1 segundo.";
                }
                else {
                    emotions = [];
                    emotionSurpriseProgress.style = "width:0%";
                    emotionSurpriseResult.innerHTML = "0%";
    
                    emotionHappyProgress.style = "width:0%";
                    emotionHappyResult.innerHTML = "0%";
    
                    emotionNeutralProgress.style = "width:0%";
                    emotionNeutralResult.innerHTML = "0%";
    
                    emotionDisgustProgress.style = "width:0%";
                    emotionDisgustResult.innerHTML = "0%";
    
                    emotionSadProgress.style = "width:0%";
                    emotionSadResult.innerHTML = "0%";
    
                    emotionAngryProgress.style = "width:0%";
                    emotionAngryResult.innerHTML = "0%";
    
                    emotionFearProgress.style = "width:0%";
                    emotionFearResult.innerHTML = "0%";
    
                    emotionStatus.innerHTML = "Nenhum rosto detectado.";
                }
                setTimeout(() => { requestAnimationFrame(trackFace) }, 1000);
            }
    
            /*
                Evento OnClick do Botão 'Habilitar câmera' (#enable-camera):
                - Inicializa a captura da câmera 
            */
            btnEnableCamera.addEventListener('click', function (e) {
                //Inicializa a captura da câmera 
                startWebcam(camera)
            })  
        </script>

