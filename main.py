import cv2
import numpy as np

def main():
    GRID_SIZE = 16  # adjustable grid size

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    window_name = "WebcamRand"
    # Create a normal window (resizable)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # Hide toolbar and go fullscreen
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        h, w, _ = frame.shape

        # --- Extract center square ---
        side = min(h, w)
        y1 = (h - side) // 2
        x1 = (w - side) // 2
        square = frame[y1:y1 + side, x1:x1 + side]

        # --- Pixelate to GRID_SIZE x GRID_SIZE ---
        pixelated_center_square = cv2.resize(square, (GRID_SIZE, GRID_SIZE), interpolation=cv2.INTER_LINEAR)
        pixelated_center_square_gray = cv2.cvtColor(pixelated_center_square, cv2.COLOR_BGR2GRAY)

        # --- Pixelated full-size for top-right ---
        pixelated = cv2.resize(pixelated_center_square, (w, h), interpolation=cv2.INTER_NEAREST)
        pixelated_gray = cv2.cvtColor(pixelated, cv2.COLOR_BGR2GRAY)
        pixelated_gray = cv2.cvtColor(pixelated_gray, cv2.COLOR_GRAY2BGR)

        # --- Build canvas ---
        canvas_h = h * 2
        canvas_w = w * 2
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        canvas[0:h, 0:w] = frame
        canvas[0:h, w:w*2] = pixelated_gray

        # --- Bottom-left numbers ---
        bottom_height = h
        bottom_width = w
        cell_h = bottom_height // GRID_SIZE
        cell_w = bottom_width // GRID_SIZE

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(cell_h, cell_w) / 40
        thickness = 2

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                val = pixelated_center_square_gray[i, j]
                x = j * cell_w
                y = h + i * cell_h + int(cell_h * 0.7)
                text = f"{val:3}"
                (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                cv2.rectangle(canvas, (x, y - text_h), (x + text_w, y + baseline), (0, 0, 0), -1)
                cv2.putText(canvas, text, (x, y), font, font_scale, (255, 255, 255), thickness)

        # --- Bottom-right large integer ---
        flat_bytes = pixelated_center_square_gray.flatten().tolist()
        byte_array = bytes(flat_bytes)
        large_int = int.from_bytes(byte_array, byteorder='big')
        text = str(large_int)
        max_chars_per_line = 40
        lines = [text[i:i+max_chars_per_line] for i in range(0, len(text), max_chars_per_line)]

        font_scale_br = 1.0
        thickness_br = 2
        for idx, line in enumerate(lines):
            (text_w, text_h), baseline = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale_br, thickness_br)
            x = w + (bottom_width - text_w) // 2
            total_text_height = len(lines) * (text_h + 5)
            y = h + ((bottom_height - total_text_height) // 2) + idx * (text_h + 5) + text_h
            cv2.putText(canvas, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale_br, (255, 255, 255), thickness_br)

        cv2.imshow(window_name, canvas)

        # Quit if 'q' pressed or window closed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
