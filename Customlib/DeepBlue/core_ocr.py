# -*- coding: utf-8 -*-
"""
deepblue.core_ocr

This module provides functions to perform Optical Character
Recognition (OCR) on images, extracting text content 
for further processing.
"""

import os
import tempfile

from paddleocr import PaddleOCR
from PIL import Image
from .config import LANGUAGE, DOC_ORIENTATION, DOC_UNWARPING, TEXTLINE_ORIENTATION

# Preprocessing scale factor (fraction of original size). 0.5 == 50% of the
# longest side. Configurable via config.py (OCR_SCALE). Set to 1.0 for no
# downscale, lower values shrink the image before OCR for speed.
OCR_SCALE = 0.5

class DeepBlueOCR:

    def __init__(
        self, 
        lang: str = LANGUAGE,
        use_doc_orientation_classify: bool = DOC_ORIENTATION,
        use_doc_unwarping: bool = DOC_UNWARPING,
        use_textline_orientation: bool = TEXTLINE_ORIENTATION,
        ) -> None:

        self.lang = lang
        self.use_doc_orientation_classify = use_doc_orientation_classify
        self.use_doc_unwarping = use_doc_unwarping
        self.use_textline_orientation = use_textline_orientation

    def _preprocess(self, image_path: str):
        if not os.path.exists(image_path):
            return image_path
        try:
            with Image.open(image_path) as im:
                im = im.convert("RGB")
                if OCR_SCALE and 0 < OCR_SCALE < 1:
                    nw = max(1, int(round(im.width * OCR_SCALE)))
                    nh = max(1, int(round(im.height * OCR_SCALE)))
                elif OCR_SCALE and OCR_SCALE >= 1:
                    nw, nh = im.width, im.height
                else:
                    nw, nh = im.width, im.height
                im = im.resize((nw, nh), Image.LANCZOS)
                fd, tmp = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                im.save(tmp)
                return tmp
        except Exception:
            return image_path

    def _build(self) -> None:
        self.ocr = PaddleOCR(
            lang=self.lang,
            use_doc_orientation_classify=self.use_doc_orientation_classify,
            use_doc_unwarping=self.use_doc_unwarping,
            use_textline_orientation=self.use_textline_orientation,
            enable_mkldnn=False,
        )

    def predict(self, image_path: str):
        if not hasattr(self, 'ocr'):
            self._build()
        tmp = self._preprocess(image_path)
        try:
            return self.ocr.predict(tmp)
        finally:
            if tmp != image_path and os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass
    
    def release(self):
        if hasattr(self, 'ocr'):
            del self.ocr
