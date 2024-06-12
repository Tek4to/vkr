import copy
import os
import re
from heapq import nlargest

import cv2
import numpy as np
import tifffile as tiff
import torch
from PIL.Image import Image

from tifffile import TiffFileError
import cv2 as cv



class TrackingModel:

    def __init__(self, model_path: str):
        self.load(model_path)
        self.out = None

    def load(self, model_path: str) -> None:
        self._model = torch.hub.load('.', 'custom', path=model_path, source='local',)


    @staticmethod
    def IoU(box1, box2):
        x1, y1, x2, y2 = box1[0]
        x3, y3, x4, y4 = box2
        if x1 > x4:
            return 0
        if x2 < x3:
            return 0
        if y1 > y4:
            return 0
        if y2 < y3:
            return 0
        x_inter1 = max(x1, x3)
        y_inter1 = max(y1, y3)
        x_inter2 = min(x2, x4)
        y_inter2 = min(y2, y4)
        width_inter = abs(x_inter2 - x_inter1)
        height_inter = abs(y_inter2 - y_inter1)
        area_inter = width_inter * height_inter
        width_box1 = abs(x2 - x1)
        height_box1 = abs(y2 - y1)
        width_box2 = abs(x4 - x3)
        height_box2 = abs(y4 - y3)
        area_box1 = width_box1 * height_box1
        area_box2 = width_box2 * height_box2
        area_union = area_box1 + area_box2 - area_inter
        value = area_inter / area_union
        if value > 1:
            value = 0
        return value

    def predict(self, path: str) -> object:
        data = self.preprocessing(path)
        res = self._model(data).xyxy
        result = self.process(res, data)
        self.out = result
        return self.out

    def process(self, result, data):
        array = []
        flag = False
        # Blue color in BGR
        color = (255, 0, 0)
        # Line thickness of 2 px
        thickness = 2
        start_point = (0, 0)
        end_point = (0, 0)
        for number, img in enumerate(result):
            img = img.numpy().tolist()
            if len(img) > 0:
                flag = True
                if len(img) > 1:
                    img = img[1]
                else:
                    img = img[0]
                start_point = (int(img[0]), int(img[1]))
                end_point = (int(img[2]), int(img[3]))
                image = data[number]
                cv2.rectangle(image, start_point, end_point, color, thickness)
                array.append(image)
            elif flag:
                image = data[number]
                cv2.rectangle(image, start_point, end_point, color, thickness)
                array.append(image)
        array = self.convertToTiff(array, out_image='test2.tif')
        return array

    def postProcess(self, result):
        res = copy.deepcopy(result)
        box = 0, 0, 0, 0
        number = None
        # Поиск первого обнаружения узла
        for stat, image in enumerate(result):
            scores = image[1]['detection_scores']
            boxes = image[1]['detection_boxes']
            score = max(scores)
            if score >= 0.3:
                index = np.where(scores == score)
                box = boxes[index]
                number = stat
                res[stat][1]['detection_scores'] = np.array(score).reshape(1, )
                res[stat][1]['detection_boxes'] = box
                break
        stop_score = 0.1
        tracker_score = 0.4
        # Отсеивание лишних боксов
        if number is None:
            return None
        for i in range(number + 1, len(result)):
            iou = []
            boxes1 = result[i][1]['detection_boxes']
            scores1 = result[i][1]['detection_scores']
            max_score = max(scores1)
            if max_score < 0.2:
                flagScore = False
            else:
                flagScore = True
            box_max_score = boxes1[np.where(scores1 == max_score)]
            if not flagScore:
                res[i][1]['detection_boxes'] = box_max_score
                res[i][1]['detection_scores'] = np.array(stop_score).reshape(1, )
                continue
            for j in range(len(boxes1)):
                iou.append(self.IoU(box, boxes1[j]))
            iou_max = nlargest(5, iou)
            index_iou = []
            for k in range(len(iou_max)):
                if iou_max[k] < 0.5:
                    continue
                index_iou.append(np.where(iou == iou_max[k]))
            if len(index_iou) == 0:
                flagIOU = False
            else:
                flagIOU = True
            box1 = []
            max_score_iou = self.IoU(box, box_max_score[0])
            for l in index_iou:
                box1.append(boxes1[l])
            if len(boxes1) == 1:
                box1.append(boxes1)
            if max_score_iou >= 0.5:
                box1.append(box_max_score)
            box1 = np.array(box1)
            x1 = np.mean([a[0][0] for a in box1])
            y1 = np.mean([a[0][1] for a in box1])
            x2 = np.mean([a[0][2] for a in box1])
            y2 = np.mean([a[0][3] for a in box1])
            box = np.array([x1, y1, x2, y2]).reshape(1, 4)
            if max_score_iou < 0.5:
                res[i][1]['detection_boxes'] = box
            else:
                res[i][1]['detection_boxes'] = box_max_score
            score = []
            for u in index_iou:
                score.append(res[i][1]['detection_scores'][u])
            if max_score_iou >= 0.5:
                score.append(np.array(max_score).reshape(1, ))
            if max_score_iou < 0.5:
                res[i][1]['detection_scores'] = np.array(tracker_score).reshape(1, )
            else:
                res[i][1]['detection_scores'] = np.array(max_score).reshape(1, )
        return res


if __name__ == '__main__':
    tif_path = 'data/25_TIRADS3_cross.tif'
    tracking_model = TrackingModel(model_path='all_long_model.pt')
    tracking_model.predict(path=tif_path)
