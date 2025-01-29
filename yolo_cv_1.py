import cv2
import torch
import numpy as np

# Load YOLOv5 model
def load_model(model_path='yolov5s.pt'):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
    model.conf = 0.4  # Set confidence threshold for faster inference
    model.iou = 0.45  # Set IoU threshold for non-max suppression
    return model

# Perform object detection
def detect_objects(model, frame):
    results = model(frame, size=200)  # Use smaller input size for faster inference
    detections = results.xyxy[0].cpu().numpy()  # Bounding boxes and confidence scores
    return detections

# Draw bounding boxes and labels on the frame
def draw_detections(frame, detections, class_names):
    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = f"{class_names[int(cls)]} {conf:.2f}"
        color = (0, 255, 0)
        
        # Draw bounding box
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        
        # Draw label
        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Main function
def main():
    # Load YOLOv5 model
    model = load_model()
    class_names = model.names  # Get class names

    # Initialize video capture
    cap = cv2.VideoCapture(0)  # Use webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    cap.set(cv2.CAP_PROP_FPS, 24)

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    print("Press 'q' to exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        # Convert frame to RGB (torch model requires RGB input)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform object detection
        detections = detect_objects(model, frame_rgb)

        # Draw detections on the frame
        draw_detections(frame, detections, class_names)

        # Display the frame
        cv2.imshow('Object Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()