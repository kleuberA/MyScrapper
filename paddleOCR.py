import cv2
from paddleocr import PaddleOCR
import csv
from datetime import datetime
import numpy as np
import threading

# Função para capturar a imagem da webcam
def capture_frame():
    global frame
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Falha ao capturar imagem")
            break
        cv2.imshow("Webcam", frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):  # Pressione 'q' para sair
            break
        elif key == ord('s'):  # Pressione 's' para capturar a imagem
            print("Imagem capturada!")
            break
        
    cap.release()
    cv2.destroyAllWindows()

# Iniciar a captura da webcam em uma thread
thread = threading.Thread(target=capture_frame)
thread.start()

# Esperar a thread capturar a imagem
thread.join()

# Inicializar o PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='pt')

# Processar a imagem capturada com PaddleOCR
result = ocr.ocr(frame, cls=True)

# Exibir resultados brutos
print("Resultados do OCR:")
for line in result:
    print(line)

# Função para extrair as informações da tabela nutricional
def extract_nutritional_info(result):
    # Inicializar um dicionário para armazenar as informações nutricionais
    nutritional_info = {}
    
    # Filtrar as linhas com os dados que possam estar relacionados aos valores nutricionais
    for line in result:
        text = line[1][0].lower()  # Corrigido: agora acessamos diretamente a string da linha
        # Você pode ajustar as palavras-chave conforme necessário
        if 'energia' in text or 'carboidrato' in text or 'proteína' in text or 'gordura' in text:
            print(f"Encontrado: {line[1][0]}")
            nutritional_info[line[1][0]] = line[1][1]  # Adiciona a chave e o valor encontrado
    
    return nutritional_info

# Extrair a tabela nutricional
nutritional_data = extract_nutritional_info(result)

# Mostrar as informações nutricionais extraídas
print("\nInformações Nutricionais extraídas:")
for nutrient, value in nutritional_data.items():
    print(f"{nutrient}: {value}")

# Se você quiser salvar os dados em um arquivo CSV
filename = "tabela_nutricional.csv"
header = ["Nutriente", "Valor"]

# Salvar as informações extraídas em um arquivo CSV
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for nutrient, value in nutritional_data.items():
        writer.writerow([nutrient, value])

print(f"\nTabela nutricional salva em {filename}")
