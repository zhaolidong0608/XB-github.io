from flask import Flask, render_template, request, jsonify
from ly_api import LingyiAPI
import os
import io
import json
import base64

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from PIL import Image
    HAS_IMAGE = True
except ImportError:
    HAS_IMAGE = False

app = Flask(__name__)
ly_api = LingyiAPI()


def extract_text_from_pdf(file_stream):
    if not HAS_PDF:
        return ""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF提取错误: {e}")
        return ""


def get_image_info(file_stream, filename):
    if not HAS_IMAGE:
        return f"图片文件名: {filename}\n"
    try:
        img = Image.open(file_stream)
        info = f"图片文件名: {filename}\n"
        info += f"图片尺寸: {img.size[0]} x {img.size[1]}\n"
        info += f"图片格式: {img.format}\n"
        info += f"图片模式: {img.mode}\n"
        return info
    except Exception as e:
        print(f"图片信息提取错误: {e}")
        return f"图片文件名: {filename}\n"


def image_to_base64(file_stream):
    try:
        file_stream.seek(0)
        image_data = file_stream.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return base64_data
    except Exception as e:
        print(f"图片转base64错误: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify({'success': True, 'models': ly_api.get_model_configs()})


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        mode = request.form.get('mode', 'health_qa')
        text_input = request.form.get('text', '')
        files = request.files.getlist('files')
        
        image_base64 = None
        if files and len(files) > 0:
            image_file = files[0]
            file_stream = io.BytesIO(image_file.read())
            image_base64 = image_to_base64(file_stream)
        
        result = ly_api.generic_chat(mode, text_input, image_base64)
        
        if result.get('error_code') == 0:
            results_list = result.get('result', [])
            if results_list:
                first_result = results_list[0]
                messages = first_result.get('messages', [])
                if messages:
                    message = messages[0]
                    content = message.get('content', [])
                    if content:
                        response_text = content[0].get('body', '')
                        return jsonify({'success': True, 'report': response_text})
        
        return jsonify({'success': False, 'error': result.get('message', '未知错误'), 'result': result})
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})


@app.route('/api/chat_stream', methods=['POST'])
def chat_stream():
    try:
        mode = request.form.get('mode', 'health_qa')
        text_input = request.form.get('text', '')
        files = request.files.getlist('files')
        
        image_base64 = None
        if files and len(files) > 0:
            image_file = files[0]
            file_stream = io.BytesIO(image_file.read())
            image_base64 = image_to_base64(file_stream)
        
        def generate():
            full_text = ""
            try:
                for data in ly_api.generic_chat(mode, text_input, image_base64, stream=True):
                    if data.get('error_code') == 0:
                        results_list = data.get('result', [])
                        if results_list:
                            first_result = results_list[0]
                            messages_list = first_result.get('messages', [])
                            if messages_list:
                                message = messages_list[0]
                                content = message.get('content', [])
                                if content:
                                    text = content[0].get('body', '')
                                    if text:
                                        if len(text) > len(full_text):
                                            full_text = text
                                        else:
                                            full_text += text
                                        yield f"data: {json.dumps({'text': full_text}, ensure_ascii=False)}\n\n"
            except Exception as e:
                import traceback
                error_info = f"错误: {str(e)}\n堆栈: {traceback.format_exc()}"
                print(error_info)
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return app.response_class(generate(), mimetype='text/event-stream')
    except Exception as e:
        import traceback
        error_info = f"错误: {str(e)}\n堆栈: {traceback.format_exc()}"
        print(error_info)
        def error_generate():
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        return app.response_class(error_generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
