from flask import Flask, request, jsonify
import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS
from utils.ocr import ocr_image
from utils.LLM import ask_deepseek
from collections import Counter
import re
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/uploadFlowChartApi', methods=['POST'])
def upload_image():
    data = request.json 
    if 'image_base64' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    image_data = data['image_base64']
    
    if image_data.startswith('data:image/'):
        image_data = image_data.split(',')[1] 

    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    ocr_message = ocr_image(image) 
    
    return jsonify({'message': 'Image received and processed successfully', 'ocr_message': ocr_message}), 200 
    
@app.route('/uploadPdfTextApi', methods=['POST'])
def upload_pdf_text():
    data = request.json
    text = data['pdf_text']
    ocr_result = data['ocr_result']
    words = ''
    for i,result in enumerate(ocr_result):
        words += f'{i}:' + result[1]+', '
    print(words)
    output_example = "knowledge_graph = [[parentIndex, childIndex, parent, child] ... ]"
    prompt = text+'根据这篇文章建立'+words+'这些词的知识图谱。输出知识图谱结构部分每个父子关系带索引的Python列表knowledge_graph,输出如：'+ output_example
    response = ask_deepseek(prompt)
    # print(response)
    pattern = r'\[(\d+), (\d+), "([^"]+)", "([^"]+)"\]'
    graph_data = re.findall(pattern, response) 
    parents = [data[0] for data in graph_data] 
    center_degree = Counter(parents)
    centers = [key for key, value in center_degree.items() if value > 1]
    print(centers)
    node_list = []
    temp_id_list = []
    for data in graph_data: 
        if data[0] not in temp_id_list :
            degree = center_degree[data[0]] if center_degree[data[0]] else 0
            center = data[0]
            node_list.append([data[0], data[2],degree,center])
            temp_id_list.append(data[0])
        if data[1] not in temp_id_list:
            degree = center_degree[data[1]] if center_degree[data[1]] else 0
            center =  data[1] if data[1] in centers else data[0]
            node_list.append([data[1], data[3],degree,center])
            temp_id_list.append(data[1])
    del temp_id_list
    if graph_data:
        return jsonify({'graph_data': graph_data,'node_list':node_list,'centers':centers}), 200
    else:
        return jsonify({'graph_data': None}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444, debug=True)