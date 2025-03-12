import io
import base64
def image_to_base64(img):
    # 创建一个字节流对象
    buffered = io.BytesIO()
    
    # 将图片保存到字节流
    img.save(buffered, format="PNG")
    
    # 获取字节流中的数据
    img_bytes = buffered.getvalue()
    
    # 转换为 Base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64