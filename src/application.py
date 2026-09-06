"""Controle da câmera, seleção da ROI e interface OpenCV."""

import cv2 as cv
import imutils
import numpy as np

from config import CAMERA_INDICES, FRAME_WIDTH
from preprocessing import preprocess_image, remove_noise
from recognition import process_display
from stabilization import ReadingStabilizer


MAIN_WINDOW = "SSOCR - Webcam Feed"
DEBUG_WINDOW = "Threshold Limpo (Debug)"
ROI_WINDOW = "Selecione o Display"

Region = tuple[int, int, int, int]


def open_camera(indices: tuple[int, ...]) -> tuple[cv.VideoCapture | None, int | None]:
    """Abre a primeira câmera disponível dentre os índices configurados."""
    for index in indices:
        capture = cv.VideoCapture(index)

        if capture.isOpened():
            return capture, index

        capture.release()
        print(f"[AVISO] Câmera no índice {index} não respondeu.")

    return None, None


def print_instructions(camera_index: int) -> None:
    """Exibe os comandos disponíveis no terminal."""
    print(f"\n=== SSOCR Estabilizado — Câmera USB (Índice {camera_index}) ===")
    print("-> Posicione o visor na câmera e aperte 'S' para selecionar.")
    print("-> Aperte 'R' para resetar a seleção.")
    print("-> Aperte 'Q' para fechar.\n")


def draw_selection_message(output: np.ndarray) -> None:
    """Informa que a região do display ainda deve ser selecionada."""
    cv.putText(
        output,
        "Pressione 'S' para selecionar o ROI",
        (15, 30),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
    )


def process_roi(
    frame: np.ndarray,
    output: np.ndarray,
    roi: Region,
    stabilizer: ReadingStabilizer,
) -> None:
    """Processa a região selecionada e desenha a leitura reconhecida."""
    x, y, width, height = roi
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    roi_image = gray_frame[y:y + height, x:x + width]

    threshold = preprocess_image(roi_image)
    threshold = remove_noise(threshold)

    current_reading = process_display(threshold, output, x, y)
    stable_reading = stabilizer.update(current_reading)

    label_bottom = max(y, 30)
    cv.rectangle(
        output,
        (x, label_bottom - 30),
        (x + width, label_bottom),
        (0, 0, 0),
        -1,
    )
    cv.putText(
        output,
        f"Leitura: {stable_reading}",
        (x + 5, label_bottom - 8),
        cv.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )
    cv.rectangle(
        output,
        (x, y),
        (x + width, y + height),
        (255, 100, 0),
        1,
    )
    cv.imshow(DEBUG_WINDOW, threshold)


def select_roi(frame: np.ndarray) -> Region | None:
    """Solicita ao usuário a seleção da região do display."""
    selected = cv.selectROI(ROI_WINDOW, frame, False)
    cv.destroyWindow(ROI_WINDOW)

    x, y, width, height = map(int, selected)
    if width > 0 and height > 0:
        return x, y, width, height

    return None


def close_debug_window() -> None:
    """Fecha a janela de depuração caso ela esteja aberta."""
    try:
        cv.destroyWindow(DEBUG_WINDOW)
    except cv.error:
        pass


def process_frames(capture: cv.VideoCapture) -> None:
    """Executa o laço principal de captura e tratamento dos comandos."""
    roi: Region | None = None
    stabilizer = ReadingStabilizer()

    while True:
        success, frame = capture.read()

        if not success:
            print("[ERRO] Não foi possível capturar um quadro da câmera.")
            break

        frame = imutils.resize(frame, width=FRAME_WIDTH)
        output = frame.copy()

        if roi is None:
            draw_selection_message(output)
        else:
            process_roi(frame, output, roi, stabilizer)

        cv.imshow(MAIN_WINDOW, output)
        key = cv.waitKey(1) & 0xFF

        if key == ord("s"):
            new_roi = select_roi(frame)

            if new_roi is not None:
                roi = new_roi
                stabilizer.reset()

        elif key == ord("r"):
            roi = None
            stabilizer.reset()
            close_debug_window()

        elif key == ord("q"):
            break


def run() -> None:
    """Inicializa a câmera e executa a aplicação."""
    capture, camera_index = open_camera(CAMERA_INDICES)

    if capture is None or camera_index is None:
        print("[ERRO] Nenhuma câmera USB externa encontrada.")
        return

    print_instructions(camera_index)

    try:
        process_frames(capture)
    finally:
        capture.release()
        cv.destroyAllWindows()
