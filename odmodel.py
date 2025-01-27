##### Using the raspberry pi to detect people in security camera pictures
#
# Author: Sahas Munamala
# Date: 4/5/2020
# Description:
# This object of this program is to detect which images from the security camera 
# contain people. Currently, the camera sends an email every time movement is detected.
# Howver, I do not want to get emails of my neighbor's cat every day, so this program
# will run every image through a tensorflow model to detect if people are present.
# The program will be running 24/7 on a raspberry pi.

import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import logging

logging.basicConfig(filename='logs/model.log', level=logging.INFO, format='%(asctime)s : %(levelname)s: %(message)s')

from utils import label_map_util

THRESHOLD = 0.5

class odmodel :
    """
    This class abstracts the tensorflow model so its main functions
    can be used without concern for the lower-level implementation
    """
    def __init__ (self) :

        self.MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
        self.CWD_PATH = os.getcwd()

        self.PATH_TO_CKPT = os.path.join(self.CWD_PATH,self.MODEL_NAME,'frozen_inference_graph.pb')
        self.PATH_TO_LABELS = os.path.join(self.CWD_PATH,'data','mscoco_label_map.pbtxt')
        self.NUM_CLASSES = 90

        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, \
                max_num_classes=self.NUM_CLASSES, \
                use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)

        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=detection_graph)

        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    def _runmodel (self, frame_expanded, frame) :
        print( "Running model" )
        (boxes, scores, classes, num) = self.sess.run([self.detection_boxes, \
                self.detection_scores, \
                self.detection_classes, \
                self.num_detections], \
                feed_dict={self.image_tensor: frame_expanded})
        return (boxes, scores, classes, num)

    def runimage (self, imagefile) :
        frame = cv2.imread(imagefile, cv2.IMREAD_COLOR)
        frame.setflags(write=1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_expanded = np.expand_dims(frame_rgb, axis=0)

        (boxes, scores, classes, num) = self._runmodel(frame_expanded, frame)

    def findPerson (self, imagefile) :
        """Find a person in a given image
        Run imagefile through object detection model and parse the output for
        indication of a person

        Parameters:
        imagefile   : filesystem path to image to process

        Returns:
        True    : Person has been detected in image
        False   : No Person inside the image
        """
        frame = cv2.imread(imagefile, cv2.IMREAD_COLOR)
        frame.setflags(write=1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_expanded = np.expand_dims(frame_rgb, axis=0)

        (boxes, scores, classes, num) = self._runmodel(frame_expanded, frame)

        if (classes is not None) :
            confidence = scores[0,0]
            logging.info("confidence: %f" % confidence)
            if confidence > THRESHOLD:
                logging.info("person detected")
                return True
        return False



if __name__ == "__main__" :
    odm = odmodel()
    (boxes, scores, classes, num) = odm.run_image('/home/sahas/Desktop/Wallpapers/nomanssky2.jpg')
    print("finished model" )

