import io
import os
from google.cloud import vision_v1p3beta1 as vision
import cv2
import re
from utils.smartparkingws import cadastrar_veiculo_estacionado, alterar_veiculo_estacionado, pegar_data_hora_atual


# Setup google authen client key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_key.json'

# Source path content all images
SOURCE_PATH = 'imagens\\'


def entrada_saida_estacionamento(placa, vaga, tipo, entrada=None):
    if not entrada:
        entrada = pegar_data_hora_atual()[2]
    saida = pegar_data_hora_atual()[2]
    if tipo == "E":
        print(cadastrar_veiculo_estacionado(vaga, placa, entrada))
    elif tipo == "S":
        print(alterar_veiculo_estacionado(placa, saida))


def placa_regex(texto):
    texto = texto.replace("\n", "")
    regex1 = re.compile(r'(\D{3})-(\d{4})')
    regex2 = re.compile(r'(\D{3}) (\d{4})')
    regex3 = re.compile(r'(\D{3})(\d{4})')
    placa = regex1.search(texto)
    if placa:
        # letras = placa.group(1)
        # numeros = placa.group(2)
        # completa = placa.group()
        # print(f"placa-Letras: {letras}\nPlaca-Numeros: {numeros}\nPlaca: {completa}")
        return placa.group()
    else:
        placa = regex2.search(texto)
        if placa:
            return placa.group(1) + '-' + placa.group(2)
        else:
            placa = regex3.search(texto)
            if placa:
                return placa.group(1) + '-' + placa.group(2)
            return False


def colocar_informacoes_imagem(img, vaga, hora, placa, tipo):
    if tipo == "E":
        tipo = "ENTRADA"
    elif tipo == "S":
        tipo = "SAIDA"
    height, width = img.shape[:2]
    cv2.rectangle(img, (0, 0), (width, 65), (255,255,255), -1)
    cv2.putText(img, f"VAGA: {vaga}", (5, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (204, 0, 0), 1)
    cv2.putText(img, f"{tipo}:{hora}", (5, 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (204, 0, 0), 1)
    cv2.putText(img, f"PLACA: {placa}", (5, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (204, 0, 0), 1)


def recognize_license_plate(img_path, vaga, entrada_saida):
    # Read image with opencv
    img = cv2.imread(img_path)

    # Scale image
    # img = cv2.resize(img, None, fx=.8, fy=.8)

    # Show the origin image
    cv2.imshow('Original', img)

    # Save the image to temp file
    cv2.imwrite(SOURCE_PATH + 'output.jpg', img)

    # Create new img path for google vision
    img_path = SOURCE_PATH + 'output.jpg'

    # Create google vision client
    client = vision.ImageAnnotatorClient()

    # Read image file
    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Recognize text
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # placas_encontradas = [{'placa': None, 'vaga': None}]
    placas_encontradas = []
    for text in texts:
        placa = placa_regex(text.description)
        if placa and placa not in placas_encontradas:
            placas_encontradas.append(placa)
            hora, entrada = pegar_data_hora_atual()[1], pegar_data_hora_atual()[2]
            colocar_informacoes_imagem(img, vaga, hora, placa, entrada_saida)
            entrada_saida_estacionamento(placa, vaga=vaga, entrada=entrada, tipo=entrada_saida)

            vertices = [(vertex.x, vertex.y)
                        for vertex in text.bounding_poly.vertices]

            # Draw rectangle around license plate
            cv2.rectangle(img,
                          (vertices[0][0] - 10, vertices[0][1] - 10), (vertices[2][0] + 10, vertices[2][1] + 10),
                          (0, 255, 0),
                          3, cv2.LINE_AA)
            cv2.imshow('Reconhecimento', img)
            # placas_encontradas.append({'vaga': 'TN1'})

    # for placa in placas_encontradas:
    #     entrada_saida_estacionamento(placa['placa'], placa['vaga'])

    key = cv2.waitKey(0) & 0xFF
    if key == 27:
        cv2.destroyAllWindows()

