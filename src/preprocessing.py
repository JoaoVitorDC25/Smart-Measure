import cv2 as cv
import imutils
import numpy as np

from config import MEDIAN_BLUR, ADAPTIVE_BLOCK_SIZE, ADAPTIVE_C, FINAL_MEDIAN_KERNEL, VERTICAL_CLOSE_KERNEL,VERTICAL_CLOSE_ITERATIONS, DILATION_KERNEL, DILATION_ITERATIONS

"""Operações de pré-processamento da região do display."""

def preprocess_image(warped: np.ndarray) -> np.ndarray:
    """Converte a imagem em uma máscara binária adequada aos segmentos."""
    
    if warped.size == 0:
        raise ValueError("A região de interesse está vazia.")
    
    processed = cv.medianBlur(warped, MEDIAN_BLUR) #<- Mediana
    processed = cv.normalize(processed, None, 0, 255, cv.NORM_MINMAX) #<- Normalização
    threshold = cv.adaptiveThreshold(processed,255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, ADAPTIVE_BLOCK_SIZE, ADAPTIVE_C,) #<- Binarização adaptativa
    
    # Inverte a imagem, caso o fundo fique branco
    if cv.countNonZero(threshold) > threshold.size / 2:
        threshold = cv.bitwise_not(threshold)
    
    return cv.medianBlur(threshold, FINAL_MEDIAN_KERNEL)

def remove_noise(threshold: np.ndarray) -> np.ndarray:
    """Remove contornos espúrios e recupera partes dos segmentos."""
    cleaned = threshold.copy()
    contours = imutils.grab_contours(
        cv.findContours(cleaned.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE))
    
    for contour in contours:
        _, _, width, _ = cv.boundingRect(contour)
        if (cv.contourArea(contour) < 15 or width > 150):
            cv.drawContours( cleaned, [contour], -1, 0, -1)
    
    # for contour in contours:
    #     if cv.contourArea(contour) < 15 or cv.boundingRect(contour)[2] > 150:
    #         cv.drawContours(cleaned, [contour], -1, 0, -1)
    
    # Une partes separadas verticalmente.
    vertical_kernel = cv.getStructuringElement(
        cv.MORPH_RECT,
        VERTICAL_CLOSE_KERNEL
    )

    cleaned = cv.morphologyEx(
        cleaned,
        cv.MORPH_CLOSE,
        vertical_kernel,
        iterations=VERTICAL_CLOSE_ITERATIONS
    )

    
    # Dilata para recuperar partes apagadas demais
    kernel = np.ones((2,2), np.uint8)
    return cv.dilate(cleaned, kernel, iterations=DILATION_ITERATIONS)

