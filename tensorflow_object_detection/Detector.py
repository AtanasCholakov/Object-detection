import cv2, time, os, tensorflow as tf
import numpy as np

from tensorflow.python.keras.utils.data_utils import get_file

np.random.seed(20)

class Detector:
    def __init__(self):
        pass

    def readClasses(self, classesFilePath):
        with open(classesFilePath, 'r') as f:
            self.classesList = f.read().splitlines()

        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))

    def downloadModel(self, modelURL):
         
         fileName = os.path.basename(modelURL)
         self.modelName = fileName[:fileName.index('.')]

         self.cacheDir = "./pretrained_models"

         os.makedirs(self.cacheDir, exist_ok=True)

         get_file(fname=fileName, origin=modelURL, cache_dir=self.cacheDir, cache_subdir="checkpoints", extract=True)

    def loadModel(self):
        print("Loadin Model " + self.modelName)
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cacheDir, "checkpoints", self.modelName, "saved_model"))

        print("Model" + self.modelName + " loaded successfully...")

    def createBoundingBox(self, image, threshold = 0.5):
        inputTensor = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        inputTensor = tf.convert_to_tensor(inputTensor, dtype=tf.uint8)
        inputTensor = inputTensor[tf.newaxis,...]

        detections = self.model(inputTensor)

        bboxs = detections['detection_boxes'][0].numpy()
        classIndexes = detections['detection_classes'][0].numpy().astype(np.int32)
        classScores = detections['detection_scores'][0].numpy()

        imH, imW, imC = image.shape

        bboxIdx = tf.image.non_max_suppression(bboxs, classScores, max_output_size=50, iou_threshold=threshold, score_threshold=threshold)

        print(bboxIdx)

        if len(bboxIdx) != 0:
            for i in bboxIdx:
                bbox = tuple(bboxs[i].tolist())
                classConfidence = round(100*classScores[i])
                classIndex = classIndexes[i]

                classLabelText = self.classesList[classIndex].upper()
                classColor = self.colorList[classIndex]

                displayText = '{}: {}%'.format(classLabelText, classConfidence)

                ymin, xmin, ymax, xmax = bbox

                xmin, xmax, ymin, ymax = (xmin * imW, xmax * imW, ymin * imH, ymax * imH)
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color=classColor, thickness=1)
                cv2.putText(image, displayText, (xmin, ymin -10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 2)

                lineWidth = min(int((xmax - xmin) * 0.2), int((ymax - ymin) * 0.2))

                cv2.line(image, (xmin, ymin), (xmin + lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmin, ymin), (xmin, ymin + lineWidth), classColor, thickness=5)

                cv2.line(image, (xmax, ymin), (xmax - lineWidth, ymin), classColor, thickness=5)
                cv2.line(image, (xmax, ymin), (xmax, ymin + lineWidth), classColor, thickness=5)

                cv2.line(image, (xmin, ymax), (xmin + lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmin, ymax), (xmin, ymax - lineWidth), classColor, thickness=5)

                cv2.line(image, (xmax, ymax), (xmax - lineWidth, ymax), classColor, thickness=5)
                cv2.line(image, (xmax, ymax), (xmax, ymax - lineWidth), classColor, thickness=5)

        return image


    def predictImage(self, imagePath, threshold = 0.5):
        image = cv2.imread(imagePath)

        bboxImage = self.createBoundingBox(image, threshold)

        cv2.imwrite(self.modelName + ".jpg", bboxImage)
        cv2.imshow("Result", bboxImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def predictVideo(self, videoPath, threshold = 0.5):
        cap = cv2.VideoCapture(videoPath)

        if (cap.isOpened() == False):
            print("Error opening file...")
            return
        
        (success, image) = cap.read()

        while success:
            bboxImage = self.createBoundingBox(image, threshold)

            cv2.imshow("Result", bboxImage)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            (success, image) = cap.read()
            
    def detectMovingObjects(self, videoPath):
        alpha = 0.1
        cap = cv2.VideoCapture(videoPath)

        if not cap.isOpened():
            print("Error opening file...")
            return

        (success, image) = cap.read()

        background = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.uint8)

        while success:

            current_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.uint8)
            if current_frame.shape == background.shape:
                current_frame = current_frame.astype(np.uint8)
                background = background.astype(np.uint8)
                
                diff = cv2.absdiff(current_frame, background)

                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) > 3000:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

                cv2.imshow("Moving Objects", image)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

                (success, image) = cap.read()
                
                background = alpha * current_frame + (1 - alpha) * background

            else:
                print("Sizes did not match.")
        cap.release()
        cv2.destroyAllWindows()
