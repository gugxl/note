# 本地部署 Deepseek + RagFlow 构建知识库

出现原因:绝对的隐私保护和个性化知识库构建
通过:Deepseek的本地化部署来解决隐私问题.
通过RAG(Retrieval-Augmented Generation 检索增强技术)构建知识库,需要的条件:
1. 本地部署RAG需要开源框架：RAGFlow

docker run -it --rm --gpus=all --ipc=host -p 7860:7860 -e HF_ENDPOINT=https://hf-mirror.com hiyouga/llamafactory:latest python -m src.llamafactory.cli webui --host 0.0.0.0 --port 7860