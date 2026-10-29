import cv2
import numpy as np


def improve_face_image(image):

    if image is None or image.size == 0:
        raise ValueError("Invalid or empty image")

    # 1. Improve brightness using adaptive gamma correction
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)

    if mean_brightness < 100:
        gamma = 0.7  # Brighten dark images
    elif mean_brightness > 180:
        gamma = 1.2  # Reduce excessive brightness
    else:
        gamma = 1.0  # Keep normal brightness

    # Build lookup table for faster gamma correction
    lookup = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype(
        "uint8"
    )

    bright = cv2.LUT(image, lookup)

    # 2. Improve local contrast using CLAHE
    lab = cv2.cvtColor(bright, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    enhanced = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    # 3. Reduce noise while preserving edges
    denoised = cv2.bilateralFilter(enhanced, d=5, sigmaColor=35, sigmaSpace=35)

    # 4. Sharpen slightly blurry images
    blurred = cv2.GaussianBlur(denoised, (0, 0), sigmaX=1.0)

    sharpened = cv2.addWeighted(denoised, 1.5, blurred, -0.5, 0)

    return sharpened


# Test with one image
image = cv2.imread("MY_image.jpg")

if image is not None:
    improved = improve_face_image(image)

    # Compare original and improved images
    comparison = np.hstack((image, improved))
    cv2.imshow("Original | Improved", comparison)

    cv2.imshow("improved_face", improved)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Image not found. Check the file path.")
