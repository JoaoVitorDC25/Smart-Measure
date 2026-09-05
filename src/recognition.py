"""Detecção de dígitos e leitura dos sete segmentos."""

from collections.abc import Sequence

import cv2 as cv
import imutils
import numpy as np
from imutils import contours as contour_utils

from config import DIGIT_MIN_WIDTH, DIGIT_MAX_WIDTH, DIGIT_MIN_HEIGHT, DIGIT_MAX_HEIGHT, SEGMENT_WIDTH_RATIO, SEGMENT_HEIGHT_RATIO, MIDDLE_SEGMENT_RATIO, ACTIVATION_RATIO

# ----- Dicionário de padrões de segmentos para dígitos -----
DIGITS_LOOKUP = {
    #(0, 1, 2, 3, 4, 5, 6): digit
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 0, 1, 0, 1): 1,
    (0, 1, 0, 0, 0, 1, 0): 1,
    (0, 1, 0, 0, 1, 0, 0): 1,
    (1, 0, 1, 1, 1, 0, 1): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1): 5,
    (1, 1, 0, 1, 1, 1, 1): 6,
    (1, 0, 1, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9
}

def filter_digit_contours(contours: Sequence[np.ndarray]) -> list[np.ndarray]:
    """Mantém apenas contornos com dimensões compatíveis com dígitos."""
    digit_contours = []
    for contour in contours:
        _, _, width, height = cv.boundingRect(contour)
        if (DIGIT_MIN_WIDTH <= width <= DIGIT_MAX_WIDTH and
            DIGIT_MIN_HEIGHT <= height <= DIGIT_MAX_HEIGHT):
            digit_contours.append(contour)

    if not digit_contours:
        return []

    digit_contours = contour_utils.sort_contours(digit_contours, method="left-to-right")[0]
    return digit_contours

def analyze_segments(digit_roi: np.ndarray) -> int | str:
    """Retorna o dígito correspondente ao padrão de segmentos detectado."""
    roi_height, roi_width = digit_roi.shape
    
    segment_width = int(roi_width * SEGMENT_WIDTH_RATIO)
    segment_height = int(roi_height * SEGMENT_HEIGHT_RATIO)
    middle_adjustment = int(roi_height * MIDDLE_SEGMENT_RATIO)

    segments = [
        ((0, 0), 
         (roi_width, segment_height)),                          # Seg0 — barra horizontal superior                       
        ((0, 0), 
         (segment_width, roi_height // 2)),                     # Seg1 — barra vertical superior esquerda
        ((roi_width - segment_width, 0), 
         (roi_width, roi_height // 2)),                         # Seg2 — barra vertical superior direita
        ((0, (roi_height // 2) - middle_adjustment), 
         (roi_width, (roi_height // 2) + middle_adjustment)),   # Seg3 — barra horizontal do meio
        ((0, roi_height // 2), 
         (segment_width, roi_height)),                          # Seg4 — barra vertical inferior esquerda
        ((roi_width - segment_width, roi_height // 2), 
         (roi_width, roi_height)),                              # Seg5 — barra vertical inferior direita
        ((0, roi_height - segment_height), 
         (roi_width, roi_height)),                              # Seg6 — barra horizontal inferior
    ]

    active_segments = [0] * len(segments)
    
    for index, ((x_start, y_start), (x_end, y_end)) in enumerate(segments):
        segment_roi = digit_roi[y_start:y_end, x_start:x_end]
        area = (x_end - x_start) * (y_end - y_start)
        if area and cv.countNonZero(segment_roi) / float(area) > ACTIVATION_RATIO:
            active_segments[index] = 1

    return DIGITS_LOOKUP.get(tuple(active_segments), "?")