from PIL import Image, ImageFile
import pytesseract
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
            custom_config = r'--oem 3 --psm 6 -l por+eng'
            img = self._safe_open_image(image_path)
            text = pytesseract.image_to_string(img, config=custom_config)
            return self._parse_inventory_text(text)
        except Exception as e:
            raise RuntimeError(f"Erro no OCR: {str(e)}")

    def _safe_open_image(self, image_path):
        """Abre e redimensiona imagens grandes"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", Image.DecompressionBombWarning)
            img = Image.open(image_path)
            if img.width > 3840 or img.height > 2160:
                img = img.resize((img.width//2, img.height//2), Image.LANCZOS)
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

        for line in lines:
            line = line.strip()
            if any(x in line.lower() for x in ['contagem', 'responsavel', 'pagina', 'estoque central']):
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