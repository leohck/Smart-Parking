import cv2
from utils.placa import recognize_license_plate


VIDEOS_PATH = "videos\\"


def tirar_foto(frame, dimensoes, file_name, vaga, entrada_saida="E"):
    """
    Lida com o registro de fotos
    :param vaga:
    :param frame numpy.ndarray = O frame de onde a foto deve ser registrada
    :param dimensoes numpy.ndarray = As dimensoes (x,y,w,h) para criar um novo frame a apartir das dimensoes informadas
    :param file_name str = O nome do arquivo para salvar a imagem
    :return None
    :rtype None
    """
    (x, y, w, h) = dimensoes[0], dimensoes[1], dimensoes[2], dimensoes[3]
    file = f"imagens/{file_name}.png"
    imagem = frame[y:y + h, x:x + w]
    cv2.imwrite(file, imagem)
    print(f'foto salva -> {file_name}')

    print("detectando placa....")
    recognize_license_plate(file, vaga, entrada_saida)
    print("fim detecção placa")


def mostrar_vaga(frame, roi, status="vazia", retangulo_preenchido=False):
    x, y, w, h = roi
    verde = (0, 204, 0)
    vermelho = (0, 0, 255)
    verde_preenchido = (77, 255, 136)
    vermelho_preenchido = (51, 51, 255)

    if status == "vazia":
        if retangulo_preenchido:
            cor = verde_preenchido
        else:
            cor = verde
    elif status == "ocupada":
        if retangulo_preenchido:
            cor = vermelho_preenchido
        else:
            cor = vermelho
    else:
        cor = verde

    if retangulo_preenchido:
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), cor, -1)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    else:
        cv2.rectangle(frame, (x, y), (x + w, y + h), cor, 4)


def detectar_vagas(frame):
    # roivaga1 = cv2.selectROI('roi', frame, showCrosshair=False)
    roivaga1 = (157, 212, 241, 193)
    rv1x, rv1y, rv1w, rv1h = roivaga1
    # roivaga2 = cv2.selectROI('roi', frame, showCrosshair=False)
    roivaga2 = (408, 212, 222, 187)
    rv2x, rv2y, rv2w, rv2h = roivaga2

    vaga1 = frame[rv1y:rv1y + rv1h, rv1x: rv1x+rv1w]
    mostrar_vaga(frame, roivaga1, "vazia", False)

    vaga2 = frame[rv2y:rv2y + rv2h, rv2x: rv2x+rv2w]
    mostrar_vaga(frame, roivaga2, "vazia", False)

    return vaga1, vaga2


def main():
    car_classificador = cv2.CascadeClassifier('cascades/haarcascade_parkingspace.xml')
    camera = cv2.VideoCapture(VIDEOS_PATH + 'entrando_re_perto.mp4', 0)
    reproduzir = False  # se True o video ja inicia sendo reproduzido
    detectar_carros = False  # se True o video ja inicia detectando carros
    mostrar_comandos = True  # se False nao aparece o menu com os comandos
    habilitar_comandos = True  # se False os comandos não funcionam apenas o ESC para encerrar o programa
    carro_vaga1 = 0
    carro_vaga2 = 0
    while True:
        retval, frame = camera.read()

        if not retval:
            exit()
        frame = cv2.resize(frame, None, fx=1, fy=1)

        roivaga1 = (157, 212, 241, 193)

        roivaga2 = (408, 212, 222, 187)

        vagas = detectar_vagas(frame)

        if mostrar_comandos:
            width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            frame = cv2.rectangle(frame, (0, 0), (int(width), int(height / 15)), (255, 255, 255), -1)
            comandos = "s - iniciar | p - pausar | e - encerrar"
            comandos2 = "d-detectar/pausar | f-foto (e-cancelar|s-salvar)"
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL
            cv2.putText(frame, comandos, (10, int(height / 40)), font, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, comandos2, (10, int(height / 18)), font, 1, (0, 0, 0), 1, cv2.LINE_AA)

        if habilitar_comandos:
            if not reproduzir:
                key = cv2.waitKey(0) & 0xFF
                if key == ord('s'):
                    print('tecla s -> reprodução do video iniciada')
                    reproduzir = True
                elif key == ord('e'):
                    print('tecla e -> reprodução do video encerrada')
                    break
            else:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('p'):
                    print('tecla p -> reprodução do video pausada')
                    reproduzir = False

                if key == ord('d'):
                    if detectar_carros:
                        print('tecla d -> detecção de veiculos encerrada')
                        detectar_carros = False
                    else:
                        print('tecla d -> detecção de veiculos iniciada')
                        detectar_carros = True

                if key == ord('e'):
                    print('tecla e -> reprodução do video encerrada')
                    break
        else:
            key = cv2.waitKey(1)
            if key == 27:
                break

        if detectar_carros:

            vaga1gray = cv2.cvtColor(vagas[0], cv2.COLOR_BGR2GRAY)
            vaga2gray = cv2.cvtColor(vagas[1], cv2.COLOR_BGR2GRAY)

            # carrosvaga1 = car_classificador.detectMultiScale(vaga1gray, 1.4, 2)
            carrosvaga2 = car_classificador.detectMultiScale(vaga2gray, minNeighbors=5, minSize=(90, 90))
            for carro in carrosvaga2:
                if carro.all():
                    (x, y, w, h) = carro[0], carro[1], carro[2], carro[3]
                    mostrar_vaga(frame, roivaga2, status="ocupada", retangulo_preenchido=False)
                    carro_vaga2 += 1
                    if carro_vaga2 >= 30:
                        key = cv2.waitKey(0)
                        if key == ord('f'):
                            tirar_foto(frame, roivaga2, x, "TN2")

        cv2.imshow('Detector de carros', frame)

    camera.release()
    cv2.destroyAllWindows()


main()
