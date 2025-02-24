import cv2
import pytesseract
import pandas as pd

class OCRProcessor:
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def process_image(self, image_path):
        # Carregar imagem
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Melhorar contraste
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Extrair texto
        texto = pytesseract.image_to_string(thresh, lang='por')
        
        # Processar texto em DataFrame
        linhas = [linha.split() for linha in texto.split('\n') if linha.strip()]
        dados = []
        for linha in linhas:
            if linha[0].isdigit() and len(linha) >= 4:  # Exemplo: linhas com código numérico
                item = {
                    "codigo": linha[0],
                    "nome": ' '.join(linha[1:-2]),
                    "minimo": linha[-2],
                    "contagem": linha[-1]
                }
                dados.append(item)
        
        return pd.DataFrame(dados)