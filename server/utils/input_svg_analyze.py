import xml.etree.ElementTree as ET
import re

def find_bg(svg_str,scale):
    # 解析SVG字符串
    root = ET.fromstring(svg_str)
    patternId = None
    paddingX = 0
    paddingY = 0
    bg_width = 0
    bg_height = 0
    imageUrl = None
    for g in root.findall(".//{http://www.w3.org/2000/svg}g"):
        transform = g.get("transform")
        if transform:
            path = g.find(".//{http://www.w3.org/2000/svg}path")
            # 提取路径数据 
            fill = path.get("fill")
            if fill!='none':
                patternId = re.search(r'url\(#(.*?)\)', fill)
                paddingX, paddingY = map(float, transform.split("translate(")[1].split(")")[0].split(","))
                paddingX = paddingX*scale
                paddingY = paddingY*scale
                print(patternId.group(1),paddingX,paddingY)
                break
                
    defs = root.find(".//{http://www.w3.org/2000/svg}defs")
    for pattern in defs.findall(".//{http://www.w3.org/2000/svg}pattern"):
        if pattern.get("id") == patternId.group(1):
            bg_height = float(pattern.get("height"))*scale
            bg_width = float(pattern.get("width"))*scale
            image_element = pattern.find(".//{http://www.w3.org/2000/svg}image", namespaces={"xlink": "http://www.w3.org/1999/xlink"})
            if image_element is not None:
                imageUrl = image_element.get("{http://www.w3.org/1999/xlink}href")
            break
            
    return imageUrl, paddingX, paddingY, bg_width, bg_height
def find_rect(svg_str,scale): 
    # 解析SVG字符串
    root = ET.fromstring(svg_str)
    result = []
    # 遍历所有 <g> 元素
    for g in root.findall(".//{http://www.w3.org/2000/svg}g"):
        # 检查是否有 transform 属性
        transform = g.get("transform")
        if transform:
            # 提取 transform 中的平移值 (x, y)
            if "translate" in transform:
                x, y = map(float, transform.split("translate(")[1].split(")")[0].split(","))
            else:
                x, y = 0, 0

            # 遍历 <g> 内的 <path> 元素
            for path in g.findall(".//{http://www.w3.org/2000/svg}path"):
                # 提取路径数据
                d = path.get("d")
                fill = path.get("fill")
                if fill=='none':
                    # 解析路径数据，提取宽高
                    numbers = re.findall(r'\d+\.\d+|\d+', d) 
                    width = float(numbers[4])
                    height = float(numbers[5])
                    result.append([[x*scale, y*scale], [(width+x)*scale, (height+y)*scale]])
    return result

 