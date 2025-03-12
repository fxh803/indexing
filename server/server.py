from flask import Flask, request, jsonify
import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS
from utils.ocr import *
from utils.LLM import *
from collections import Counter
import re
import json
import requests
from utils.input_svg_analyze import *
from utils.image_process import *
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/uploadFlowChartApi', methods=['POST'])
def upload_flowChart_api():
    data = request.json 
    if 'svg' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    svg = data['svg']
    canvas_width = float(data['canvas_width'])
    canvas_height = float(data['canvas_height'])
    root = ET.fromstring(svg)
    svg_width = float(root.attrib.get('width'))
    svg_height = float(root.attrib.get('height')) 
    if (canvas_width/svg_width) < (canvas_height/svg_height):
        scale = canvas_width / svg_width
        offsetHeight  = (canvas_height - svg_height*scale)/2
        offsetWidth  = 0
    else:
        scale = canvas_height / svg_height
        offsetHeight = 0
        offsetWidth  = (canvas_width - svg_width*scale)/2
    rects = find_rect(svg,scale)
    bgUrl, paddingX, paddingY, bg_width, bg_height = find_bg(svg,scale)
    response = requests.get(bgUrl)
    if response.status_code == 200:  # 确保请求成功
        bg_image = Image.open(BytesIO(response.content))  # 读取图片
        bg_base64 = image_to_base64(bg_image)
        ocr_message,uni_ocr_message = ocr_image(bg_image) 
        
        # resized_bg_image = bg_image.resize((int(bg_width),int(bg_height)), Image.Resampling.LANCZOS)
        
        img_width, img_height = bg_image.size
        img_width_scale = bg_width / img_width
        img_height_scale = bg_height / img_height
        #把cor结果缩放一下
        for ocr in ocr_message:
            [leftTop,rightBottom] = ocr[0]
            ocr[0] = [[leftTop[0]*img_width_scale,leftTop[1]*img_height_scale],[rightBottom[0]*img_width_scale, rightBottom[1]*img_height_scale]]
        #将cor结果的坐标调整一下
        for ocr in ocr_message:
            [leftTop,rightBottom] = ocr[0]
            ocr[0] = [[leftTop[0]+paddingX,leftTop[1]+paddingY],[rightBottom[0]+paddingX, rightBottom[1]+paddingY]]
        #将每一个rect赋予一个ocr结果
        for rect in rects:
            for ocr in ocr_message:
                if rectangles_intersect_or_touch(ocr[0],rect):
                    rect.append(ocr[1])  
                    break
            if len(rect) == 2:#如果rect没有ocr结果，则检查非相交ocr结果
                for ocr in ocr_message:
                    size_of_this_rect =  rect[1][1] - rect[0][1] 
                    if rectangles_distance(ocr[0],rect) < size_of_this_rect*1.5:
                        rect.append(ocr[1])
                        break
                        
        return jsonify({'message': 'Image received and processed successfully', 
        'uni_ocr_message':uni_ocr_message,'ocr_message': ocr_message,'rects':rects,'img':bg_base64,
        'offsetHeight':offsetHeight,'offsetWidth':offsetWidth,'img_width':bg_width, 'img_height':bg_height}), 200 
    else:
        return jsonify({'error': 'Failed to download image'}), 500
@app.route('/generateKnowledgeGraphApi', methods=['POST'])
def generate_knowledge_graph_api():
    data = request.json
    text = data['pdf_text']
    keywords = data['keywords']  
    prompt = text + f"Based on this article, construct a knowledge graph of these keywords:{keywords}. return the answer as quickly as possible" 
    response = ask_deepseek_about_knowledgeGraph(prompt)
    print(response)
    # Parse the JSON string into a dictionary
    response_dict = json.loads(response)
    return jsonify({'nodes': response_dict['nodes'],'edges':response_dict['edges']}), 200 

@app.route('/findEntitiesApi', methods=['POST'])
def find_entities_api():
    data = request.json
    sentences = data['sentences']
    keywords = data['keywords']
    input = ''
    for sentence in sentences:
        key = sentence[0]
        value = sentence[1]
        input += f"The keyword '{key}' has related sentences: {', '.join(value)}. "
    question = f"{input}. Based on the above, output contextual word information for the keywords: {keywords}. Get a relationship in one sentence and return the answer as quickly as possible." 
    response = ask_deepseek_about_contextual_words(question)
    print(response)
    response_dict = json.loads(response)
    return jsonify({ 'edges': response_dict['edges'] }), 200

# @app.route('/generateIntrodutionApi', methods=['POST'])
# def generate_introdution_api():
#     data = request.json
#     sentences = data['sentences'] 
#     keyword = data['keyword']
#     print(sentences,keyword)
#     input = ''
#     for sentence in sentences:
#         input += sentence  
#     prompt =  input + f"根据上述句子， 输出关于{keyword}的作用"
#     response = ask_deepseek(prompt)
#     print(response)
#     return jsonify({ 'response': response }), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444, debug=True)