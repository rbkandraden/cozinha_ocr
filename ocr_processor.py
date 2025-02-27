from PIL import Image, ImageFile
import pytesseract
import cv2
import numpy as np
import os
import re
import pandas as pd
import warnings
from flask import current_app

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 200_000_000

class OCRProcessor:
    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif os.environ.get('TESSERACT_PATH'):
            pytesseract.pytesseract.tesseract_cmd = os.environ['TESSERACT_PATH']

    def process_inventory_table(self, image_path):
        """Processa imagem de tabela de estoque"""
        try:
            custom_config = r'--oem 1 --psm 4 -l por+eng'
            img = self._preprocess_image(image_path)
            text = pytesseract.image_to_string(img, config=custom_config)
            return self._parse_inventory_text(text)
        except Exception as e:
            raise RuntimeError(f"Erro no OCR: {str(e)}")

    def _preprocess_image(self, image_path):
        """Pré-processa a imagem para melhorar o OCR"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", Image.DecompressionBombWarning)
            
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2), interpolation=cv2.INTER_AREA)
            img = cv2.GaussianBlur(img, (5, 5), 0)
            img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
            
            return img

    def _parse_inventory_text(self, text):
        """Interpreta o texto extraído"""
        current_app.logger.debug(f"Texto cru do OCR:\n{text}")
        
        lines = text.split('\n')
        data = []
        
        pattern = re.compile(
            r'(?:COD\:?\s*)?(\d{3,5})?[\s\-|]*'          # Código opcional
            r'([A-Za-zÀ-ú\s\/]+?)\s*[\|]?\s*'            # Nome do item
            r'(\d+[\.,]?\d*)\s*([A-Za-z]{1,4})[\s|]+'    # Mínimo e unidade
            r'(\d+[\.,]?\d*)\s*([A-Za-z]{1,4})'          # Estoque e unidade
        )
        
        stopwords = {"contagem", "responsavel", "pagina", "estoque central"}
        
        for line in lines:
            line = re.sub(r'[^A-Za-z0-9À-ú\s|,.-]', '', line).strip()
            
            if any(x in line.lower() for x in stopwords):
                continue
            
            match = pattern.search(line)
            if match:
                _, nome, minimo, unid_min, estoque, unid_est = match.groups()
                
                if not nome.strip() or not minimo or not estoque:
                    continue
                    
                data.append({
                    "nome": self._clean_name(nome),
                    "quantidade_minima": self._convert_quantity(minimo),
                    "quantidade_atual": self._convert_quantity(estoque),
                    "unidade": self._normalize_unit(unid_est or unid_min)
                })
        
        current_app.logger.info(f"Dados parseados: {data}")
        return pd.DataFrame(data)

    def _clean_name(self, name):
        return re.sub(r'\s{2,}', ' ', name.strip()).title()

    def _convert_quantity(self, value):
        try:
            return float(str(value).replace(',', '.').strip(' kgKG'))
        except:
            return 0.0

    def _normalize_unit(self, unit):
        unit_map = {'KG': 'KG', 'GR': 'KG', 'G': 'KG',
                    'LT': 'L', 'ML': 'L',
                    'UN': 'UND', 'PC': 'UND', 'CX': 'UND'}
        return unit_map.get(unit.upper(), 'UND')
