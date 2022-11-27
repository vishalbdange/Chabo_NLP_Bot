# from easyocr import Reader
import argparse 
import cv2
import numpy as np


def imageToText(imageFile):

    print("Hi in image to text")
    # langs = ['en']
    # image = cv2.imread(imageFile)
    # print("[INFO] Performing OCR on input image...")
    # reader = Reader(langs,gpu=False)
    # results = reader.readtext(image)
    whole_text = ""
    # for(bbox,text,prob) in  results:
    #     whole_text += text + ' '
    return whole_text

