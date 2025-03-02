from flask import Flask, request, jsonify
import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS
from utils.ocr import ocr_image
from utils.LLM import *
from collections import Counter
import re
import json
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/uploadFlowChartApi', methods=['POST'])
def upload_flowChart_api():
    data = request.json 
    if 'image_base64' not in data:
        return jsonify({'error': 'No image data provided'}), 400

    image_data = data['image_base64']
    
    if image_data.startswith('data:image/'):
        image_data = image_data.split(',')[1] 

    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    ocr_message,uni_ocr_message = ocr_image(image) 
    
    return jsonify({'message': 'Image received and processed successfully', 'uni_ocr_message':uni_ocr_message,'ocr_message': ocr_message,'img_width':width,'img_height':height}), 200 
    
@app.route('/generateKnowledgeGraphApi', methods=['POST'])
def generate_knowledge_graph_api():
    data = request.json
    text = data['pdf_text']
    keywords = data['keywords']  
    prompt = text + f"Based on this article, construct a knowledge graph of these keywords:{keywords}" 
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
    question = f"{input}. Based on the above, output all contextual word information for the keywords: {keywords}." 
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