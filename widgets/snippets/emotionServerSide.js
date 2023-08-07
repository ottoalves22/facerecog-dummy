<script>
        const token = '<ACCESS_TOKEN>'; // adicione aqui o seu token de aplicação

        /* Principais elementos da interface:
            - faceEmotion: <div> que engloba o componente
            - camera: <video> que exibe a captura da webcam
            - photoTaken: <canvas> que exibe a foto capturada
            - btnEnableCamera: <button> que habilita a webcam
            - btnTakePhoto: <button> que dispara a captura da foto
            - btnConfirmPhoto: <button> que confirma a captura da foto
            - btnTakeNewPhoto: <button> que permite capturar uma nova foto
        */
        let faceEmotion = document.getElementById('face-emotion')

        let photoCamera = document.getElementById('photo-camera')
        let camera = photoCamera.querySelector('video');
        let photoTaken = photoCamera.querySelector('canvas');

        let btnEnableCamera = document.getElementById('enable-camera');
        let btnTakePhoto = document.getElementById('take-photo');
        let btnConfirmPhoto = document.getElementById('confirm-photo');
        let btnTakeNewPhoto = document.getElementById('take-new-photo');


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


        /*  
            function b64toBlob(dataURI)
            - Converve uma string na base64 em um objeto blob.
    
            Parâmetros:
            - dataURI: recebe uma string na base 64.

            Retorno da função: um objeto do tipo blob.
        */
        function b64toBlob(dataURI) {
            var byteString = atob(dataURI.split(',')[1]);
            var ab = new ArrayBuffer(byteString.length);
            var ia = new Uint8Array(ab);

            for (var i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            return new Blob([ab], { type: 'image/jpeg' });
        }


        /*  
            function startWebcam(videoElement)
            - Inicializa a captura da câmera, pedindo permissão para acesso à câmera. Caso a permissão for negada, exibe-se uma mensagem de erro.
            
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
                btnEnableCamera.classList.add('hidden');
                btnTakePhoto.classList.remove('hidden');
            }).catch(() => {
                btnEnableCamera.classList.remove('hidden');
                btnTakePhoto.classList.add('hidden');
                alert('Não foi possível acessar a câmera');
            }).finally(() => {
                btnConfirmPhoto.classList.add('hidden');
                btnTakeNewPhoto.classList.add('hidden');
                camera.classList.remove('hidden');
                photoTaken.classList.add('hidden');
                photoTaken.classList.remove('show');
            })
        }


        /*  
            function sendData(full_name, email, document, external_cod, filename, document)
            - Insere os dados num FormData e envia para a API. 
            - Se a resposta da API for bem-sucedida, mostrar as informações na tela.
    
            Parâmetros:
            - filename: Foto do usuário
            Retorno da função: Nenhum retorno.
            - document (opcional): documento do usuário da aplicação. Ex.: 59063190000 (CPF)

        */
        function sendData(filename, document = '') {
            //Insere os dados num FormData
            let formData = new FormData();
            formData.append('filename', b64toBlob(filename), Math.random() + '.jpg');
            if (document != '' && document != '<DOCUMENT>') {
                formData.append('document', document);
              }
            //Envia os dados para a API
            
            emotionStatus.innerHTML = "Carregando dados...";
            fetch('${apiUrl}', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer '+ token }, 
                body: formData,
            })
                .then((responseData) => {
                    //Registro salvo com sucesso
                    responseData.json().then((data) => {
                        if (typeof data.surprise != "undefined") {
                            emotionSurpriseProgress.style = "width:" + Math.round(data.surprise * 100) + "%";
                            emotionSurpriseResult.innerHTML = Math.round(data.surprise * 100) + "%";

                            emotionHappyProgress.style = "width:" + Math.round(data.happy * 100) + "%";
                            emotionHappyResult.innerHTML = Math.round(data.happy * 100) + "%";

                            emotionNeutralProgress.style = "width:" + Math.round(data.neutral * 100) + "%";
                            emotionNeutralResult.innerHTML = Math.round(data.neutral * 100) + "%";

                            emotionDisgustProgress.style = "width:" + Math.round(data.disgust * 100) + "%";
                            emotionDisgustResult.innerHTML = Math.round(data.disgust * 100) + "%";

                            emotionSadProgress.style = "width:" + Math.round(data.sad * 100) + "%";
                            emotionSadResult.innerHTML = Math.round(data.sad * 100) + "%";

                            emotionAngryProgress.style = "width:" + Math.round(data.angry * 100) + "%";
                            emotionAngryResult.innerHTML = Math.round(data.angry * 100) + "%";

                            emotionFearProgress.style = "width:" + Math.round(data.fear * 100) + "%";
                            emotionFearResult.innerHTML = Math.round(data.fear * 100) + "%";      

                            emotionStatus.innerHTML = "";
                        }
                        else {
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
                    })
                }).catch((responseData) => {
                    //Erro ao tentar salvar o registro
                    alert('Não foi possível enviar os dados. Tente novamente mais tarde!');
                })
        }



        /*
            Evento OnClick do Botão 'Capturar' (#take-photo):
            - Captura a imagem atual da câmera nas mesmas medidas e exibe a foto no elemento <canvas>.
            - Desativa a câmera, oculta o elemento e exibe a foto capturada após 200ms.
            - Oculta o botão 'Capturar' e exibe os botões 'Confirmar' e 'Tirar novamente'.
        */
        btnTakePhoto.addEventListener('click', function (e) {
            photoTaken.height = camera.videoHeight;
            photoTaken.width = camera.videoWidth;
            var context = photoTaken.getContext('2d');
            context.drawImage(camera, 0, 0);

            camera.classList.add('hidden');
            photoTaken.classList.remove('hidden');

            btnTakePhoto.classList.add('hidden');
            btnConfirmPhoto.classList.remove('hidden');
            btnTakeNewPhoto.classList.remove('hidden');
            setTimeout(() => {
                photoTaken.classList.add('show');
            }, 200)
        })




        /*
            Evento OnClick do Botão 'Tirar novamente' (#take-new-photo):
            - Reseta o componente para o seu estado inicial.
            - Oculta os botões 'Confirmar' e 'Tirar novamente'.
            - Exibe o botão 'Captura'.
            - Oculta a foto capturada e ativa novamente a câmera.
        */
        btnTakeNewPhoto.addEventListener('click', function (e) {
            btnTakePhoto.classList.remove('hidden');
            btnConfirmPhoto.classList.add('hidden');
            btnTakeNewPhoto.classList.add('hidden');

            camera.classList.remove('hidden');
            photoTaken.classList.add('hidden');
            photoTaken.classList.remove('show');
        })


        /*
            Evento OnClick do Botão 'Habilitar câmera' (#enable-camera):
            - Inicializa a captura da câmera 
        */
        btnEnableCamera.addEventListener('click', function (e) {
            //Inicializa a captura da câmera 
            startWebcam(camera)
        })


        /*
            Evento OnClick do Botão 'Confirmar' (#confirm-photo):
            - Oculta os botões 'Captura', 'Confirmar' e 'Tirar novamente'.
            - Envia os dados para a API
        */
        btnConfirmPhoto.addEventListener('click', function (e) {
            btnTakePhoto.classList.add('hidden');
            btnConfirmPhoto.classList.add('hidden');
            btnTakeNewPhoto.classList.remove('hidden');
            let filename = photoTaken.toDataURL('image/jpeg', 1.0);
            const document = '<DOCUMENT>'; // adicione aqui o documento do usuário do widget

            sendData(filename, document)
        })

    </script>

