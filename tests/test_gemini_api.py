import google.generativeai as genai
import os

if __name__ == "__main__":
    # 建议使用环境变量或密钥管理服务来存储您的 API 密钥
    # 这里为了演示，我们直接写入代码，但请注意这在生产环境中不安全
    # 或者，你可以使用 os.environ.get('GOOGLE_API_KEY') 来从环境变量读取
    API_KEY = 'AIzaSyCY1doRN922LVjSkLVFmkk4VGmbRAv8Oj0'

    genai.configure(api_key=API_KEY)

    # 创建一个模型实例
    # 可用的模型包括 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro' 等
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 准备您的提示（prompt）
    prompt = "下面是一段文本也是一段评价，请告诉我这段评价是正面评价，还是一般评价，还是负面评价，你在判断完后只需要输出“正面”或“一般”或“负面”，不需要输出其他东西。文本如下：\n\n 见到妹子身材很好，长的挺漂亮，穿着吊带真迷人，一进门直接交水费，洗澡的时候我双手揉着她的奶子真带劲，后面去床上，超级会调情，用舌尖亲我的咪咪，添添我的龟头，硬了以后我就翻身吃了会奶头，然后带套开始，先是主动女上，接着正面直入，我抱着大长腿忍不住舔两口，毛不多，干净无异味，于是掰开骚逼一顿舔，老师很敏感，当我含着阴蒂又吸又舔的时候，小骚逼直接被舔喷了叫床声音很入魂，妹子的反应情绪也到位，呻吟声非常悦耳，之后又换了两个动作交货，完事帮我清理干净，我依依不舍说了再见，约好下次还会再来二刷。"

    # 调用 API 生成内容
    response = model.generate_content(prompt)

    # 打印返回的结果
    print(response.text)


