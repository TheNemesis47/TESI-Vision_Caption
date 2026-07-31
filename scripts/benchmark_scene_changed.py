from skimage.metrics import structural_similarity as ssim
import cv2
from rfdetr import RFDETRMedium
import supervision as sv
from rfdetr.assets.coco_classes import COCO_CLASSES
import time


def main():
    image1 = cv2.imread("fotoSSIM1.jpeg")
    image2 = cv2.imread("fotoSSIM2.jpeg")

    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    t0 = time.perf_counter()
    score = ssim(image1_gray, image2_gray)
    t1 = time.perf_counter()
    print("SSIM:", score)

    cv2.imwrite("grayscale1.jpeg", image1_gray)
    cv2.imwrite("grayscale2.jpeg", image2_gray)
    cv2.imshow("image1 - grayscale", image1_gray)
    cv2.imshow("image2 - grayscale", image2_gray)
    print("Premi un tasto per continuare con RF-DETR...")
    cv2.waitKey(0)
    cv2.destroyWindow("image1 - grayscale")
    cv2.destroyWindow("image2 - grayscale")

    model = RFDETRMedium()
    model.optimize_for_inference(True)

    t3 = time.perf_counter()
    detections = model.predict("fotoSSIM1.jpeg", threshold=0.5)
    detections2 = model.predict("fotoSSIM2.jpeg", threshold=0.5)
    t4 = time.perf_counter()

    labels = [f"{COCO_CLASSES[class_id]}" for class_id in detections.class_id]
    annotated_image = sv.BoxAnnotator().annotate(detections.metadata["source_image"], detections)
    annotated_image = sv.LabelAnnotator().annotate(annotated_image, detections, labels)

    cv2.imwrite("annotated1.jpeg", annotated_image)
    cv2.imshow("annotated1", annotated_image)

    labels2 = [f"{COCO_CLASSES[class_id]}" for class_id in detections2.class_id]
    annotated_image2 = sv.BoxAnnotator().annotate(detections2.metadata["source_image"], detections2)
    annotated_image2 = sv.LabelAnnotator().annotate(annotated_image2, detections2, labels2)

    cv2.imwrite("annotated2.jpeg", annotated_image2)
    cv2.imshow("annotated2", annotated_image2)

    print("tempo SSIM:", (t1-t0) * 1000, "ms")
    print("tempo RF-DETR (2 immagini):", (t4-t3) * 1000, "ms")
    print("Premi un tasto per chiudere.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

if __name__ == "__main__":
    main()
