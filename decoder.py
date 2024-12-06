import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Function to decode Data Matrix from the image
def decode_data_matrix(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Convert the image to grayscale for better processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect Data Matrix codes in the image
    decoded_objects = decode(gray)

    # Loop through all detected objects and draw the bounding box and decoded data
    for obj in decoded_objects:
        # Draw the bounding box around the detected Data Matrix code
        points = obj.polygon
        if len(points) == 4:  # If the polygon has 4 points, it's a rectangle
            pts = np.array(points, dtype=np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 2)

        # Decode the data and display it on the image
        decoded_data = obj.data.decode('utf-8')
        print(f"Decoded Data: {decoded_data}")

        # Display the decoded data text on the image
        cv2.putText(image, decoded_data, (obj.rect.left, obj.rect.top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the image with bounding boxes and decoded data
    cv2.imshow("Data Matrix Decoder", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Main function to test the decoding
if __name__ == "__main__":
    image_path = "datamatrix_sample.png"  # Replace with your Data Matrix image path
    decode_data_matrix(image_path)
