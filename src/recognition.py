"""Detecção de dígitos e leitura dos sete segmentos."""

from collections.abc import Sequence

import cv2 as cv
import imutils
import numpy as np
from imutils import contours as contour_utils

from config import DIGIT_MIN_WIDTH, DIGIT_MAX_WIDTH, DIGIT_MIN_HEIGHT, DIGIT_MAX_HEIGHT

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

