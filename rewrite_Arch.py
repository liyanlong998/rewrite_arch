# Query改写使用示例
# 导入依赖库

import requests
import os
import json

# 从环境变量中获取 API Key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions" # 请根据实际API地址调整

# 基于 prompt 生成文本
def get_completion_deepseek(prompt, model="deepseek-chat"):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "stream": False
    }
    
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]

# Query改写功能
class QueryRewriter:
    def __init__(self, model="deepseek-chat"):
        self.model = model
    def rewrite_Term_Definition_query(self, query):
        """术语与定义查询类"""
        instruction = """
你是一个智能的建筑设计规范查询优化助手。当用户的问题涉及对建筑专业术语、概念的解释时，请将其归入此类。
用户通常使用口语化词汇或简称提问。
#1 改写目标：将模糊、不规范的表述，替换为明确定义的、正式的术语。
#2 改写策略：
##2.1 识别识别用户口中的非标准词汇，对应到标准术语表。如“楼间距”对应“建筑间距”、“残疾人设施”对应“无障碍设施”。
##2.2 改写后的提问应直接询问“XXX的准确定义是什么?”或“规范中如何定义XXX?”
##2.3 若用户问题中包含多个术语，可拆分为多个清晰的问题。
#3 示例：
原问题：“什么是容积率?怎么算?”
改写后：“请给出‘容积率’的准确定义及其计算公式。”
"""
        
        prompt = f"""
### 指令 ###
{instruction}

### 用户问题 ###
{query}

### 改写后的问题 ###
"""
        
        return get_completion_deepseek(prompt, self.model)
    
    def rewrite_Classify_query(self, query):
        """分类与分级标准"""
        instruction = """
你是一个智能的建筑设计规范查询优化助手。当用户的问题涉及建筑的类型划分、等级界定、设计使用年限或气候分区归属时，请将其归入此类。
用户常描述一个具体场景，询问其“属于什么”。
#1 改写目标：将描述性场景转化为符合标准分类框架的明确问题
#2 改写策略：
##2.1 提取用户描述中的关键参数，如建筑高度、层数、使用功能、所在地气候特征。
##2.2 将参数代入标准的分类逻辑中，形成如“根据标准，[某高度]的[某类型]建筑属于哪一类？”的提问。
##2.3 对于气候分区，需将地理位置信息转化为气候区划的查询。
#3 示例：
原问题: “我这栋楼28米高,算高层吗？”
改写后: “根据标准,一栋28米高的住宅建筑属于哪类民用建筑(低层/多层/高层/超高层)?”
"""
        
        prompt = f"""
### 指令 ###
{instruction}

### 用户问题 ###
{query}

### 改写后的查询 ###
"""
        
        return get_completion_deepseek(prompt, self.model)
    
    def rewrite_Plan_Layout_query(self, query):
        """规划与布局要求类"""
        instruction = """
你是一个智能的建筑设计规范查询优化助手。当用户的问题涉及建筑与城市的关系、基地规划、道路连接、建筑间距、高度控制、突出物限制时，请将其归入此类。
问题通常围绕“能不能”、“可以怎么建”展开。
#1 改写目标：将开放式的可行性询问，转化为针对特定控制指标、边界条件或限制性规定的具体查询。
#2 改写策略：
##2.1 明确用户问题中的约束条件，如是否在道路红线内、是新建还是改造、有无历史保护区限制。
##2.2 将“能不能”的问题，转化为“在[某条件]下，[某设计]应满足什么规定/限值？”。
##2.3 具体化设计要素，如“突出多少”改为“突出深度/高度的最大允许值是多少”。
#3 示例：
原问题：“建筑阳台能凸到路上面吗？”
改写后：“在经批准的既有建筑改造工程中，凸窗在无人行道的道路上空突出时，其允许的突出深度和距地最小高度是多少？”

"""
        
        prompt = f"""
### 指令 ###
{instruction}

### 当前问题 ###
{query}

### 改写后的问题 ###
"""
        
        return get_completion_deepseek(prompt, self.model)
    
    def rewrite_Function_query(self, query):
        """功能性设计指标类"""
        instruction = """
你是一个智能的建筑设计规范查询优化助手。当用户的问题涉及建筑内部空间、构件、设施的尺寸、数量、配置比例等具体设计参数时，请将其归入此类。
用户常问“要多大”、“要几个”。
#1 改写目标：将宽泛的设计询问，转化为针对特定建筑类型、特定功能空间或特定构件的精确数值、比例或计算方法的查询
#2 改写策略：
##2.1 补充问题中缺失的前提，如建筑类型是住宅还是公建，楼梯是主要疏散楼梯还是检修楼梯
##2.2 将“大小”、“数量”等模糊词，替换为“最小宽度”、“最大高度”、“最少数量”、“配置比例”等标准用语。
##2.3 对于需计算得出的指标，提问应指向计算依据或公式。
#3 示例：
原问题：“楼梯做多宽合适？”
改写后：“供日常使用的主要公共楼梯，其梯段净宽的最小设计依据是什么（例如，按几股人流计算）？每股人流的宽度如何取值？”
"""
        
        prompt = f"""
### 指令 ###
{instruction}

### 原始问题 ###
{query}
"""

        return get_completion_deepseek(prompt, self.model)
    
    def rewrite_Security_query(self, query):
        """安全防护要求类"""
        instruction = """
你是一个智能的建筑设计规范查询优化助手。当用户的问题涉及防火、疏散、抗震、防洪、防护栏杆、防护高度、结构安全等防止人身伤害和财产损失的内容时，请将其归入此类。
用户常关注“安不安全”、“怎么防护”。
#1 改写目标：将笼统的安全担忧，转化为针对特定灾害、特定部位或特定场景的具体防护措施、安全距离或构造要求的查询。
#2 改写策略：
##2.1 识别用户关心的风险类型（火灾、坠落、碰撞等）和风险部位（楼梯、门窗、阳台、地下室等）。
##2.2 将安全问题转化为“应采取什么措施？”、“应符合什么要求？”、“最小距离/高度是多少？”等具体查询。
##2.3 对于防火问题，需提醒查阅专项规范。
#3 示例：
原问题：“栏杆要做多高才安全？”
改写后：“上人屋面以及商业建筑临开敞中庭的防护栏杆，其最小高度要求分别是多少？计算高度时，如何考虑可踏部位的影响？”
"""
        
        prompt = f"""
### 指令 ###
{instruction}

### 用户问题 ###
{query}

### 改写后的问题 ###
"""
        
        return get_completion_deepseek(prompt, self.model)
    
    def auto_rewrite_query(self, query):
        """自动识别Query类型并进行改写"""
        instruction = """
请分析用户的查询，识别其属于以下哪种类型：
1. 术语与定义查询类 - 询问专业术语、概念的解释或定义,如"什么是容积率？"、"楼梯平台的定义"
2. 分类与分级标准 - 询问建筑类型、等级、分类归属,如"多少米算高层建筑？"、"属于几类气候区"
3. 规划与布局要求类 - 询问建筑规划、间距、布局、高度控制,如"建筑间距要求"、"退红线距离"
4. 功能性设计指标类 - 询问尺寸、数量、比例等具体设计参数,如"楼梯宽度"、"房间最小面积"
5. 安全防护要求类 - 询问防火、疏散、防护栏杆等安全要求,如"栏杆高度"、"防火门要求"

请返回JSON格式的结果：
{
    "query_type": "查询类型",
    "rewritten_query": "改写后的查询",
    "confidence": "置信度(0-1)"
}
"""
        
        prompt = f"""
### 指令 ###
{instruction}

### 用户问题 ###
{query}

### 分析结果 ###
"""
        
        response = get_completion_deepseek(prompt, self.model)
        try:
            return json.loads(response)
        except:
            return {
                "query_type": "未知类型",
                "rewritten_query": query,
                "confidence": 0.5
            }
    
    def auto_rewrite_and_execute(self, query):
        """自动识别Query类型并进行改写，然后根据类型调用相应的改写方法"""
        # 首先进行自动识别
        result = self.auto_rewrite_query(query)
        
        # 记录调用的函数名称
        called_function = "unknown"
        
        # 根据识别结果调用相应的改写方法
        query_type = result.get('query_type', '')
        
        if '术语与定义查询类' in query_type:
            final_result = self.rewrite_Term_Definition_query(query)
            called_function = "rewrite_Term_Definition_query"
        elif '分类与分级标准' in query_type:
            final_result = self.rewrite_Classify_query(query)
            called_function = "rewrite_Classify_query"
        elif '规划与布局要求类' in query_type:
            final_result = self.rewrite_Plan_Layout_query(query)
            called_function = "rewrite_Plan_Layout_query"
        elif '功能性设计指标类' in query_type:
            final_result = self.rewrite_Function_query(query)
            called_function = "rewrite_Function_query"
        elif '安全防护要求' in query_type:
            final_result = self.rewrite_Security_query(query)
            called_function = "rewrite_Security_query"
        else:
            # 对于其他类型，返回自动识别的改写结果
            final_result = result.get('rewritten_query', query)
            called_function = "auto_rewrite_query (直接使用)"
        
        return {
            "original_query": query,
            "detected_type": query_type,
            "confidence": result.get('confidence', 0.5),
            "rewritten_query": final_result,
            "called_function": called_function,
            "auto_rewrite_result": result
        }

def main():
    # 初始化Query改写器
    rewriter = QueryRewriter()    

    print("示例6: 自动识别Query类型")
    test_queries = [
        "屋顶层有个放设备的空间，层高很矮，那叫啥？",
        "我这栋楼50米高，是公共建筑，算高层吗？",
        "两栋住宅楼之间要隔多远才不影响采光？",
        "楼梯多宽合适",
        "阳台栏杆要做多高才安全？"

    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"测试查询 {i}: {query}")
        result = rewriter.auto_rewrite_and_execute(query)
        print(f"  识别类型: {result['detected_type']}")
        print(f"  置信度: {result['confidence']}")
        print(f"  调用函数: {result['called_function']}")
        print(f"  改写结果: {result['rewritten_query']}\n")

    
if __name__ == "__main__":
    main()