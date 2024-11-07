# cài đặt các module cần thiết
# pip install ultralytics supervision
from ultralytics import YOLO
from PIL import Image
import supervision as sv
import numpy as np

IOU_THRESHOLD        = 0.3
CONFIDENCE_THRESHOLD = 0.2

pretrained_path = "erax_nsfw_yolo11m.pt"
image_path_list = ["img_0.jpg", "img_1.jpg"]

model = YOLO(pretrained_path)
results = model(image_path_list,
                  conf=CONFIDENCE_THRESHOLD,
                  iou=IOU_THRESHOLD
                )


for result in results:
    annotated_image = result.orig_img.copy()
    h, w = annotated_image.shape[:2]
    anchor = h if h > w else w

    # make_love class will cover entire context !!!
    # selected_classes = [0, 1, 2, 3, 4, 5] # all classes
    selected_classes = [0, 2, 3, 4, 5] # hidden make_love class
    detections = sv.Detections.from_ultralytics(result)
    detections = detections[np.isin(detections.class_id, selected_classes)]
       
    # box_annotator = sv.BoxAnnotator()
    # annotated_image = box_annotator.annotate(
    #     annotated_image,
    #     detections=detections
    # )
    
    # blur_annotator = sv.BlurAnnotator(kernel_size=anchor/50)    
    # annotated_image = blur_annotator.annotate(
    #     annotated_image.copy(),
    #     detections=detections
    # )

    label_annotator = sv.LabelAnnotator(text_color=sv.Color.BLACK,
                                        text_scale=anchor/1700)
    annotated_image = label_annotator.annotate(
        annotated_image,
        detections=detections
    )

    pixelate_annotator = sv.PixelateAnnotator(pixel_size=anchor/50)
    annotated_image = pixelate_annotator.annotate(
        scene=annotated_image.copy(),
        detections=detections
    )
    
    sv.plot_image(annotated_image, size=(10, 10))
