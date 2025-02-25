from PIL import Image, ImageFile
import pytesseract
import os
import re
import pandas as pd
import warnings

# Configurações de segurança para imagens grandes
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 200_000_000  # 200 milhões de pixels

class OCRProcessor:
   def __init__(self, tesseract_path=None):
    if not tesseract_path:
        tesseract_path = os.environ.get('TESSERACT_PATH')
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def process_inventory_table(self, image_path):
        """Processa imagem de tabela de estoque e retorna DataFrame"""
        try:
            custom_config = r'--oem 3 --psm 6 -l por+eng'
            img = self._safe_open_image(image_path)
            text = pytesseract.image_to_string(img, config=custom_config)
            return self._parse_inventory_text(text)
        except Exception as e:
            raise RuntimeError(f"Erro no OCR: {str(e)}")

    def _safe_open_image(self, image_path):
        """Abre e redimensiona imagens grandes de forma segura"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", Image.DecompressionBombWarning)
            img = Image.open(image_path)
            if img.width > 3840 or img.height > 2160:
                img = img.resize((img.width//2, img.height//2), Image.LANCZOS)
            return img

    def _parse_inventory_text(self, text):
        """Interpreta o texto extraído do OCR e estrutura os dados"""
        lines = text.split('\n')
        data = []
        
        # Padrão regex aprimorado para capturar diferentes formatos
        pattern = re.compile(
            r'(?:\bCOD:?)?\s*(\d{3,5})?[\.\-\s]*'  # Código opcional
            r'([A-Za-zÀ-ú\s\/]+?)\s+'              # Nome do item
            r'([\d\.,]+)\s*([A-Za-z]{2,4})\s+'     # Mínimo e unidade
            r'([\d\.,]+)\s*([A-Za-z]{2,4})'        # Estoque e unidade
        )

        for line in lines:
            line = line.strip()
            if not line or any(x in line for x in ['---', 'CONTAGEM', 'Página']):
                continue
            
            if match := pattern.search(line):
                codigo, nome, minimo, unid_min, estoque, unid_est = match.groups()
                data.append({
                    "nome": self._clean_name(nome),
                    "quantidade_minima": self._convert_quantity(minimo),
                    "quantidade_atual": self._convert_quantity(estoque),
                    "unidade": self._normalize_unit(unid_est or unid_min)
                })
                
        return pd.DataFrame(data)

    def _clean_name(self, name):
        """Remove caracteres indesejados e formata o nome"""
        return re.sub(r'\s{2,}', ' ', name.strip()).title()

    def _convert_quantity(self, value):
        """Converte valores com vírgula e trata caracteres especiais"""
        try:
            clean_value = str(value).replace(',', '.').translate(str.maketrans('', '', ' kgKG'))
            return float(clean_value)
        except:
            return 0.0

    def _normalize_unit(self, unit):
        """Padroniza as unidades de medida"""
        unit_map = {
            'KG': 'KG', 'GR': 'KG', 'G': 'KG',
            'LT': 'L', 'ML': 'L',
            'UN': 'UND', 'PC': 'UND', 'CX': 'UND'
        }
        return unit_map.get(unit.upper(), 'UND')