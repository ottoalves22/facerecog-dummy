<script>
        const token = '<ACCESS_TOKEN>'; // adicione aqui o seu token de aplicação

        /* Principais elementos da interface:
            - faceRecognition: <div> que engloba o componente
            - camera: <video> que exibe a captura da webcam
            - photoTaken: <canvas> que exibe a foto capturada
            - btnTakePhoto: <button> que dispara a captura da foto
            - btnConfirmPhoto: <button> que confirma a captura da foto
            - btnTakeNewPhoto: <button> que permite capturar uma nova foto
        */
        let faceRegister = document.getElementById('face-register')
        let form = faceRegister.querySelector('form')

        let faceRecognition = document.getElementById('photo-camera')
        let camera = faceRecognition.querySelector('video');
        let photoTaken = faceRecognition.querySelector('canvas');

        let btnRegister = document.getElementById('register');
        let btnEnableCamera = document.getElementById('enable-camera');
        let btnTakePhoto = document.getElementById('take-photo');
        let btnConfirmPhoto = document.getElementById('confirm-photo');
        let btnTakeNewPhoto = document.getElementById('take-new-photo');

        document.querySelectorAll(".snippet label>input").forEach(input => {
            input.addEventListener("input", function () {
                if (input.value.length > 0)
                    input.parentElement.classList.add("filled")
                else
                    input.parentElement.classList.remove("filled")
                validateRegistration()
            })
        })

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
            function sendData(full_name, email, document, external_cod, filename)
            - Insere os dados num FormData e envia para a API. 
            - Se a resposta da API for bem-sucedida, mostrar mensagem de sucesso e resetar o formulário.
    
            Parâmetros:
            - full_name: Nome do usuário
            - email: Email do usuário
            - document: Documento de identificação do usuário
            - external_cod: Código externo do usuário
            - filename: Foto do usuário
            Retorno da função: Nenhum retorno.
        */
        function sendData(full_name, email, document, external_cod, filename) {
            //Insere os dados num FormData
            let formData = new FormData();
            formData.append('full_name', full_name);
            formData.append('email', email);
            formData.append('document', document);
            formData.append('external_cod', external_cod);
            formData.append('filename', b64toBlob(filename), Math.random() + '.jpg');
            formData.append('document', cpf);

            //Envia os dados para a API
            fetch("${apiUrl}user/", {
                method: 'POST',
                headers: { 'Authorization': 'Bearer '+ token },
                body: formData,
            })
                .then((responseData) => {
                    //Registro salvo com sucesso
                    alert('Cadastro efetuado com sucesso!');
                    resetRegistration();
                }).catch((responseData) => {
                    //Erro ao tentar salvar o registro
                    alert('Não foi possível efetuar o cadastro. Tente novamente mais tarde!');
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
            Evento OnClick do Botão 'Finalizar cadastro' (#register):
            - Coleta os dados dos formulários e chama sendData() para enviar os dados para API
        */
        btnRegister.addEventListener('click', function (e) {
            let full_name = form.querySelector('[name="full_name"]').value;
            let email = form.querySelector('[name="email"]').value;
            let document = form.querySelector('[name="document"]').value;
            let external_cod = form.querySelector('[name="external_cod"]').value;
            let file_name = photoTaken.toDataURL('image/jpeg', 1.0);
            sendData(full_name, email, document, external_cod, file_name);
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
            - Valida o formulário.
        */
        btnConfirmPhoto.addEventListener('click', function (e) {
            btnTakePhoto.classList.add('hidden');
            btnConfirmPhoto.classList.add('hidden');
            btnTakeNewPhoto.classList.add('hidden');
            validateRegistration()
        })


        /*  
            function validateRegistration()
            - Valida o formulário e ativa/desativa o botão de 'Finalizar cadastro'.
    
            Parâmetros: Nenhum parâmetro.
            Retorno da função: Nenhum retorno.
        */
        function validateRegistration() {
            let valid = true;
            if (!form.checkValidity())
                valid = false;
            if (photoTaken.classList.contains("hidden"))
                valid = false;

            if (valid)
                btnRegister.removeAttribute("disabled");
            else
                btnRegister.setAttribute("disabled", true);
        }


        /*  
            function resetRegistration()
            - Reseta o formulário e os estado dos botões.
    
            Parâmetros: Nenhum parâmetro.
            Retorno da função: Nenhum retorno.
        */
        function resetRegistration() {
            form.reset();
            document.querySelectorAll(".filled").forEach(input => {
                input.classList.remove("filled");
            })

            btnTakePhoto.classList.remove('hidden');
            btnConfirmPhoto.classList.add('hidden');
            btnTakeNewPhoto.classList.add('hidden');

            camera.classList.remove('hidden');
            photoTaken.classList.add('hidden');
            photoTaken.classList.remove('show');
        }
    </script>

