import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
from typing_extensions import TypedDict
import os
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
except ImportError:
    # 如果依赖未安装，提供占位实现
    class ChatOpenAI:
        def __init__(self, **kwargs):
            pass
        
        async def ainvoke(self, messages):
            class Response:
                content = "模拟响应：依赖未安装"
            return Response()
    
    class ChatPromptTemplate:
        @staticmethod
        def from_messages(messages):
            return ChatPromptTemplateStub(messages)
    
    class ChatPromptTemplateStub:
        def __init__(self, messages):
            self.messages = messages
        
        def format_messages(self, **kwargs):
            return []
    
    def add_messages(messages, new_messages):
        return messages
    
    END = "end"
    StateGraph = None

class LLMConfig:
    """LLM配置类"""
    def __init__(self, model: str, base_url: Optional[str] = None, api_key: Optional[str] = None, temperature: float = 0.7):
        self.model = "qwen-plus"
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.temperature = temperature
    
    def create_llm(self) -> ChatOpenAI:
        """创建LLM实例"""
        kwargs = {
            "model": self.model,
            "temperature": self.temperature
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url   
        if self.api_key:
            kwargs["api_key"] = self.api_key
        return ChatOpenAI(**kwargs)

class PodcastState(TypedDict):
    """播客生成状态"""
    content: str
    content_type: Optional[str]
    voices: List[str]
    is_precise: Optional[bool]
    detailed_content: Optional[str]
    script: Optional[str]
    target_language: str
    final_script: Optional[str]
    messages: List[Any]

class PodcastScriptGenerator:
    def __init__(
        self,
        analyzer_llm_config: LLMConfig,
        content_generator_llm_config: LLMConfig,
        script_generator_llm_config: LLMConfig,
        translator_llm_config: LLMConfig
    ):
        # 为每个步骤创建不同的LLM
        self.analyzer_llm = analyzer_llm_config.create_llm()
        self.content_generator_llm = content_generator_llm_config.create_llm()
        self.script_generator_llm = script_generator_llm_config.create_llm()
        self.translator_llm = translator_llm_config.create_llm()
        
        self.graph = self._build_graph()
    
    def _validate_voices(self, voices: List[str]) -> List[str]:
        """验证并限制声音数量最多5个"""
        if len(voices) > 5:
            print(f"警告：声音数量超过5个，已截取前5个。原数量：{len(voices)}")
            return voices[:5]
        return voices
    
    def _build_graph(self) -> StateGraph:
        """构建LangChain Graph"""
        if StateGraph is None:
            # 如果依赖未安装，返回简单的占位对象
            class GraphStub:
                async def ainvoke(self, state):
                    # 简单模拟处理流程
                    state["is_precise"] = True
                    state["script"] = f"模拟脚本内容：{state['content']}"
                    state["final_script"] = state["script"]
                    return state
            return GraphStub()
        
        workflow = StateGraph(PodcastState)
        
        # 添加节点
        workflow.add_node("analyze_content", self._analyze_content_precision)
        workflow.add_node("generate_detailed_content", self._generate_detailed_content)
        workflow.add_node("generate_script", self._generate_podcast_script)
        workflow.add_node("check_language", self._check_and_translate_language)
        
        # 设置入口点
        workflow.set_entry_point("analyze_content")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "analyze_content",
            self._should_generate_detailed_content,
            {
                "generate_detailed": "generate_detailed_content",
                "direct_script": "generate_script"
            }
        )
        
        workflow.add_edge("generate_detailed_content", "generate_script")
        workflow.add_edge("generate_script", "check_language")
        workflow.add_edge("check_language", END)
        
        return workflow.compile()
    
    async def _analyze_content_precision(self, state: PodcastState) -> PodcastState:
        """使用专门的分析LLM分析内容是否精确"""
        # 验证声音数量
        validated_voices = self._validate_voices(state["voices"])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的内容分析专家。请判断给定的内容是精确的播客脚本还是模糊的主题描述。

精确脚本的特征：
- 包含具体的朗读文本内容
- 有明确的发言人和对话（如果是多人）
- 内容详细完整，可以直接朗读
- 有具体的播客结构和内容

模糊描述的特征：
- 只是主题、概念或想法
- 缺乏具体的文本内容
- 需要进一步展开成完整的朗读稿
- 只是大纲或提纲

请仔细分析内容，只回答 "precise" 或 "vague"，不要添加其他解释。"""),
            ("human", "请分析以下内容：\n{content}")
        ])
        
        response = await self.analyzer_llm.ainvoke(
            prompt.format_messages(content=state["content"])
        )
        
        is_precise = "precise" in response.content.lower()
        
        return {
            **state,
            "voices": validated_voices,
            "is_precise": is_precise,
            "messages": add_messages(state.get("messages", []), [response])
        }
    
    def _should_generate_detailed_content(self, state: PodcastState) -> str:
        """决定是否需要生成详细内容"""
        return "direct_script" if state["is_precise"] else "generate_detailed"
    
    async def _generate_detailed_content(self, state: PodcastState) -> PodcastState:
        """使用专门的内容生成LLM根据模糊描述生成详细内容"""
        voices_count = len(state["voices"])
        content_type = state.get("content_type", "通用")
        
        # 根据voices数量动态调整prompt
        if voices_count == 0:
            voice_instruction = """
生成单人朗读内容大纲（5分钟）：
- 单人朗读形式
- 直入主题，无需介绍
- 内容要简洁精炼"""
            
        elif voices_count == 1:
            voice_instruction = f"""
生成单人朗读内容大纲（5分钟）：
- 朗读者：{state['voices'][0]}
- 直入主题，无需自我介绍
- 内容要有重点，简洁明了"""
            
        else:
            voices_list = "、".join(state["voices"])
            voice_instruction = f"""
生成多人对话内容大纲（5分钟）：
- 参与者：{voices_list}
- 直接开始讨论，无需介绍环节
- 对话要简洁高效"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是一个专业的内容策划师。根据给定的主题描述，生成5分钟朗读内容的详细大纲。

内容类型：{content_type}
{voice_instruction}

请生成包含以下要素的内容大纲：

1. 核心内容（4-4.5分钟）
   - 2-3个核心要点
   - 每个要点要精炼有力
   - 包含具体例子或案例
   - 提供实用建议

2. 总结（30秒-1分钟）
   - 快速总结核心观点
   - 简短的行动建议

重要要求：
- 不要包含任何节目介绍、欢迎词、自我介绍
- 不要创建节目名称或播客信息
- 直接进入主题内容
- 内容要高度浓缩，去除冗余信息
- 语言要简洁有力，节奏要快
- 总字数控制在800-1000字左右

直接从主题内容开始，无需任何开场白。"""),
            ("human", "主题描述：{content}")
        ])
        
        response = await self.content_generator_llm.ainvoke(
            prompt.format_messages(content=state["content"])
        )
        
        return {
            **state,
            "detailed_content": response.content,
            "messages": add_messages(state.get("messages", []), [response])
        }
    
    async def _generate_podcast_script(self, state: PodcastState) -> PodcastState:
        """使用专门的脚本生成LLM生成播客脚本"""
        voices_count = len(state["voices"])
        source_content = state.get("detailed_content") or state["content"]
        
        # 根据voices数量动态调整脚本格式和要求
        if voices_count <= 1:
            voice_name = state["voices"][0] if state["voices"] else "朗读者"
            script_format = f"""
脚本格式（单人朗读，5分钟）：
直接输出朗读文本，无需标注发言人。

示例：
人工智能正在改变我们的工作方式。最明显的变化是自动化程度的提升...

这种变化带来三个关键影响。第一，重复性工作将被替代...

总结一下，面对AI时代，我们需要做好三件事...

要求：
- 直接从主题内容开始
- 不要任何开场白、问候语、自我介绍
- 不要创建节目名称
- 语言简洁有力，避免废话
- 总字数800-1000字"""
            
        else:
            voices_list = state["voices"]
            script_format = f"""
脚本格式（多人对话，5分钟）：
发言人：说话内容

示例：
{voices_list[0]}：人工智能对教育的影响主要体现在三个方面...
{voices_list[1] if len(voices_list) > 1 else "嘉宾"}：我觉得最重要的是个性化学习...
{voices_list[0]}：你能具体说说吗？
{voices_list[1] if len(voices_list) > 1 else "嘉宾"}：比如AI可以根据学生的学习进度...

要求：
- 严格使用提供的人名：{voices_list}
- 直接开始讨论主题，无需介绍环节
- 不要任何开场白、问候语
- 对话要快节奏，避免冗长
- 总字数800-1000字"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是一个专业的脚本编写师。请将给定的内容大纲转换为5分钟的纯文本朗读脚本。

{script_format}

脚本编写要求：

1. 内容要求
   - 直接从主题内容开始，无任何开场
   - 不要包含：欢迎词、问候语、自我介绍、节目介绍
   - 不要创建：节目名称、播客信息、主持人介绍
   - 每句话都要有价值，去除冗余
   - 重点突出，逻辑清晰

2. 格式要求
   - 输出纯文本格式，不使用markdown语法
   - 不要使用加粗、斜体等格式
   - 单人：直接输出朗读文本
   - 多人：严格按照"发言人：说话内容"格式
   - 发言人姓名必须与voices列表完全一致

3. 时长控制
   - 严格控制在5分钟内（800-1000字）
   - 按正常语速150-200字/分钟计算

4. 语言要求
   - 使用口语化表达，适合朗读
   - 语言简洁有力，节奏明快
   - 避免书面语和复杂句式

请生成完整的朗读脚本，直接从主题内容开始。"""),
            ("human", "参与者：{voices}\n\n请根据以下内容生成脚本：\n\n{content}")
        ])
        
        voices_str = "、".join(state["voices"]) if state["voices"] else "单人朗读"
        
        response = await self.script_generator_llm.ainvoke(
            prompt.format_messages(voices=voices_str, content=source_content)
        )
        
        return {
            **state,
            "script": response.content,
            "messages": add_messages(state.get("messages", []), [response])
        }
    
    async def _check_and_translate_language(self, state: PodcastState) -> PodcastState:
        """使用专门的翻译LLM检查并翻译语言"""
        target_language = state.get("target_language", "中文")
        script = state["script"]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是一个专业的语言检测和翻译专家。请执行以下任务：

1. 语言检测：检测给定脚本的主要语言
2. 语言匹配：判断是否与目标语言"{target_language}"一致
3. 翻译处理：如果不一致，请进行专业翻译

翻译要求（如需要）：
- 保持脚本的格式：
  * 单人脚本：保持纯文本格式
  * 多人脚本：保持"发言人：内容"格式
- 保持发言人姓名不变
- 确保翻译后的内容自然流畅，适合朗读
- 保持5分钟的时长要求（800-1000字）
- 使用目标语言的自然表达方式
- 输出纯文本格式，不使用任何markdown语法

如果语言一致，请直接返回原脚本。
如果需要翻译，请返回翻译后的完整脚本。

请只返回最终的脚本内容，不要添加任何解释或说明。"""),
            ("human", "目标语言：{target_language}\n\n脚本：\n{script}")
        ])
        response = await self.translator_llm.ainvoke(
            prompt.format_messages(target_language=target_language, script=script)
        )
        
        return {
            **state,
            "final_script": response.content,
            "messages": add_messages(state.get("messages", []), [response])
        }

async def generate_text_stream(
    content: str, 
    contentType: str = None, 
    voices: List[str] = [],
    target_language: str = "中文",
    analyzer_llm_config: LLMConfig = None,
    content_generator_llm_config: LLMConfig = None,
    script_generator_llm_config: LLMConfig = None,
    translator_llm_config: LLMConfig = None,
    db: AsyncSession = None
) -> AsyncGenerator[str, None]:
    """
    生成文本流的异步生成器函数
    
    1. 根据content判断，此内容是精确的内容，还是一个大概性的描述，如果是大概性的描述，则需要根据contentType和voices生成一个详细的内容内容
    2. 如果content是精确的内容，则调用llm生成一个播客脚本
    3. 检测脚本与目标语言是否一致，如果不一致，则需要翻译成目标语言
    4. 返回脚本
    """
    
    # 检查依赖是否已安装
    if "ChatOpenAI" not in globals() or not isinstance(ChatOpenAI, type):
        # 依赖未安装，使用简单实现
        chunks = content.split()
        for chunk in chunks:
            yield chunk + " "
        yield "\n依赖未安装，请安装所需依赖: pip install langchain-core langchain-openai langgraph"
        return
    
    # 默认LLM配置
    default_config = LLMConfig("gpt-4", temperature=0.7)
    
    generator = PodcastScriptGenerator(
        analyzer_llm_config or default_config,
        content_generator_llm_config or default_config,
        script_generator_llm_config or default_config,
        translator_llm_config or default_config
    )
    
    # 验证voices数量
    if len(voices) > 5:
        yield f"警告：声音数量超过5个限制，已自动截取前5个。\n"
        voices = voices[:5]
    
    # 初始化状态
    initial_state = PodcastState(
        content=content,
        content_type=contentType,
        voices=voices,
        target_language=target_language,
        messages=[]
    )
    
    try:
        # 执行图工作流
        result = await generator.graph.ainvoke(initial_state)
        
        # 流式返回最终脚本
        final_script = result["final_script"]
        
        # 将脚本分段流式返回，无需延迟
        paragraphs = final_script.split('\n\n')
        
        # 如果提供了数据库会话，保存脚本到数据库
        if db:
            from app.models.podcast import Podcast
            
            # 提取脚本摘要（使用前100个字符）
            summary = content[:100] + "..." if len(content) > 100 else content
            
            # 处理voice_ids格式
            voice_ids_str = ','.join(voices) if voices else ""
            


            
            # 创建新的播客记录
            new_podcast = Podcast(
                content=summary,
                voice_ids=voice_ids_str,
                transcript=final_script,
                content_type=contentType,
                title=summary
            )
            
            # 保存到数据库
            db.add(new_podcast)
            await db.commit()
            await db.refresh(new_podcast)
            
            # 返回保存成功的消息
            yield f"播客脚本已保存，ID: {new_podcast.id}\n\n"
        
        # 返回脚本内容
        for paragraph in paragraphs:
            if paragraph.strip():
                yield paragraph.strip() + "\n\n"
        
    except Exception as e:
        yield f"\n生成过程中出现错误: {str(e)}\n"