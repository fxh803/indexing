import paddleocr  # 添加: 导入paddleocr库
import numpy as np
from math import sqrt
from utils.word_analyze import analyze_text
import cv2  # 导入OpenCV库
def rectangles_intersect_or_touch(rect1, rect2):
    # 检查两个矩形是否相交或接触
    # rect1 and rect2 are in the format [left_top, right_top, right_bottom, left_bottom]
    rect1_left = rect1[0][0]
    rect1_right = rect1[1][0]
    rect1_top = rect1[0][1]
    rect1_bottom = rect1[1][1]

    rect2_left = rect2[0][0]
    rect2_right = rect2[1][0]
    rect2_top = rect2[0][1]
    rect2_bottom = rect2[1][1]

    return not (rect1_right <= rect2_left or  # rect1 is to the left of rect2
                rect1_left >= rect2_right or  # rect1 is to the right of rect2
                rect1_bottom <= rect2_top or  # rect1 is above rect2
                rect1_top >= rect2_bottom)    # rect1 is below rect2

def rectangles_distance(rect1, rect2):
    # 计算两个矩形之间的最小距离
    rect1_left = rect1[0][0]
    rect1_right = rect1[1][0]
    rect1_top = rect1[0][1]
    rect1_bottom = rect1[1][1]

    rect2_left = rect2[0][0]
    rect2_right = rect2[1][0]
    rect2_top = rect2[0][1]
    rect2_bottom = rect2[1][1]
    rect1_center_x = (rect1_left + rect1_right) / 2
    rect1_center_y  = (rect1_top + rect1_bottom) / 2
   
    rect2_center_x = (rect2_left + rect2_right) / 2
    rect2_center_y  = (rect2_top + rect2_bottom) / 2
    distance = sqrt((rect2_center_x-rect1_center_x)**2+(rect2_center_y-rect1_center_y)**2) 
    return distance

def ocr_image(image):
    numpy_image = np.array(image)
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en')  # 初始化PaddleOCR
    result = ocr.ocr(numpy_image, cls=True)  # 使用PaddleOCR进行图像识别
    processed_result = []
    for line in result[0]:
        pos_rect = [line[0][0],line[0][2]]
        processed_result.append([pos_rect, line[1][0]])

    combined_result = [] # 创建一个空的列表，用于存储合并后的结果 
    for i in range(len(processed_result)):
        if i==0:
            combined_result.append([processed_result[i][0] ,processed_result[i][1]])
            continue 
        else: 
            for j in range(len(combined_result)):
                other_rect = combined_result[j][0]
                this_rect = processed_result[i][0]
                size_of_this_rect =  this_rect[1][1] - this_rect[0][1]   
                if rectangles_intersect_or_touch(other_rect, this_rect) or rectangles_distance(other_rect, this_rect) < size_of_this_rect*1.5:
                    combined_result[j][1] += ' ' + processed_result[i][1] 
                    updated_rect = [[min(other_rect[0][0], this_rect[0][0]), min(other_rect[0][1], this_rect[0][1])], [max(other_rect[1][0], this_rect[1][0]), max(other_rect[1][1], this_rect[1][1])]]
                    combined_result[j][0] = updated_rect
                    break
                if j == len(combined_result)-1:
                    combined_result.append([processed_result[i][0] ,processed_result[i][1]])
        
    #使用OpenCV绘制矩形框并添加文本
    # for rect, text in combined_result:
    #     top_left = tuple(map(int, rect[0]))
    #     bottom_right = tuple(map(int, rect[1]))
    #     cv2.rectangle(numpy_image, top_left, bottom_right, (0, 255, 0), 2)  # 绿色矩形框，线宽2
    #     cv2.putText(numpy_image, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # 蓝色文本，字体大小0.5，线宽1
    # cv2.imwrite('test1.png', numpy_image)
    final_result = analyze_text(combined_result)
    return final_result
