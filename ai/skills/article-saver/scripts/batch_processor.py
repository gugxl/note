#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Article Saver Skill - 批量处理脚本
自动抓取微信文章并整理为标准化笔记
支持图片下载和本地化
"""

import json
import re
import os
import sys
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Optional, Union
# -*- coding: utf-8 -*-
"""
Article Saver Skill - 批量处理脚本
自动抓取微信文章并整理为标准化笔记
"""

import json
import re
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional, Union

# 配置
CONFIG_FILE = "skills/article-saver/config.json"
INDEX_FILE = "skills/article-saver/data/index.json"

class ArticleSaver:
    def __init__(self):
        self.config = self.load_config()
        self.index = self.load_index()
        
    def load_config(self) -> dict:
        """加载配置文件"""
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_index(self) -> dict:
        """加载文章索引"""
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"articles": [], "last_updated": ""}
    
    def save_index(self):
        """保存文章索引"""
        self.index["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def auto_classify(self, title: str, content: str) -> str:
        """自动分类文章"""
        text = (title + " " + content).lower()
        
        for category, info in self.config["categories"].items():
            if category == "Others":
                continue
            for keyword in info["keywords"]:
                if keyword.lower() in text:
                    return category
        
        return "Others"
    
    def extract_tags(self, title: str, content: str) -> List[str]:
        """提取标签"""
        text = (title + " " + content).lower()
        tags = []
        
        # 基于关键词提取标签
        keyword_mapping = {
            "Transformer": ["transformer", "attention"],
            "深度学习": ["深度学习", "神经网络", "deep learning"],
            "Python": ["python", "pytorch", "tensorflow"],
            "前端": ["前端", "react", "vue", "javascript"],
            "后端": ["后端", "spring", "django", "flask"],
            "算法": ["算法", "leetcode", "动态规划"],
            "架构": ["架构", "系统设计", "分布式"]
        }
        
        for tag, keywords in keyword_mapping.items():
            for kw in keywords:
                if kw in text:
                    tags.append(tag)
                    break
        
        return tags[:5]  # 最多5个标签
    
    def download_image(self, url: str, save_dir: str, prefix: str = "img") -> Optional[str]:
        """下载图片到本地目录"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            # 获取图片扩展名
            content_type = response.headers.get('Content-Type', '')
            ext = '.jpg'
            if 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            elif 'jpeg' in content_type:
                ext = '.jpeg'
            
            # 如果URL中有文件名，尝试使用
            parsed = urlparse(url)
            url_filename = os.path.basename(parsed.path)
            if url_filename and '.' in url_filename:
                url_ext = os.path.splitext(url_filename)[1]
                if url_ext and len(url_ext) <= 5:
                    ext = url_ext
            
            # 生成唯一文件名（使用URL的hash）
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{prefix}-{url_hash}{ext}"
            filepath = os.path.join(save_dir, filename)
            
            # 如果文件已存在，返回现有路径
            if os.path.exists(filepath):
                return filename
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filename
        except Exception as e:
            print(f"    下载图片失败: {url} - {str(e)}")
            return None
    
    def extract_images(self, content: str, save_dir: str, note_filename: str = "note") -> tuple:
        """提取内容中的图片URL并下载，返回处理后的内容和图片列表"""
        images = []
        
        # 查找所有图片URL
        img_patterns = [
            r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown图片 ![alt](url)
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # HTML图片 <img src="url">
            r'http://mmbiz\.qpic\.cn/[^\s"\')]+\.(jpg|jpeg|png|gif|webp)',  # 微信图片
            r'https://mmbiz\.qpic\.cn/[^\s"\')]+\.(jpg|jpeg|png|gif|webp)',  # 微信图片(https)
        ]
        
        # 提取所有图片URL
        found_urls = set()
        for pattern in img_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    url = match[-1]  # 取最后一个匹配（即URL）
                else:
                    url = match
                if url.startswith('http'):
                    found_urls.add(url)
        
        # 下载图片
        for idx, url in enumerate(found_urls):
            # 生成描述性前缀
            prefix = f"image-{idx+1:02d}"
            filename = self.download_image(url, save_dir, prefix)
            if filename:
                images.append({
                    "url": url,
                    "filename": filename,
                    "original_url": url
                })
        
        return content, images
    
    def replace_image_refs(self, content: str, images: list, note_dir: str) -> str:
        """替换内容中的图片URL为本地引用"""
        result = content
        
        for img in images:
            # 替换Markdown图片语法
            result = result.replace(img["original_url"], f"../{img['filename']}")
            result = result.replace(img["url"], f"../{img['filename']}")
        
        return result
    

    def sanitize_filename(self, title: str) -> str:
        """清理文件名"""
        # 移除特殊字符
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # 限制长度
        max_len = self.config["output"]["max_title_length"]
        if len(title) > max_len:
            title = title[:max_len]
        return title.strip()
    
    def generate_filename(self, title: str) -> str:
        """生成文件名"""
        date_str = datetime.now().strftime("%Y%m%d")
        safe_title = self.sanitize_filename(title)
        return f"{date_str}-{safe_title}.md"
    
    def load_template(self) -> str:
        """加载模板"""
        template_path = self.config["template"]["file"]
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def create_note(self, article_info: Dict) -> str:
        """创建笔记"""
        template = self.load_template()
        
        # 填充模板
        note = template.replace("{{title}}", article_info.get("title", "Untitled"))
        note = note.replace("{{source_url}}", article_info.get("url", ""))
        note = note.replace("{{author}}", article_info.get("author", "Unknown"))
        note = note.replace("{{publish_date}}", article_info.get("publish_date", ""))
        note = note.replace("{{save_date}}", datetime.now().strftime("%Y-%m-%d"))
        note = note.replace("{{category}}", article_info.get("category", "Others"))
        note = note.replace("{{tags}}", ", ".join(article_info.get("tags", [])))
        note = note.replace("{{summary}}", article_info.get("summary", "待补充..."))
        note = note.replace("{{key_points}}", article_info.get("key_points", "- 待补充要点"))
        note = note.replace("{{content}}", article_info.get("content", "待补充详细内容..."))
        note = note.replace("{{code_examples}}", article_info.get("code", "```\n# 待补充代码示例\n```"))
        note = note.replace("{{explanation}}", "待补充重点解析...")
        note = note.replace("{{personal_notes}}", "<!-- 在这里写下你的思考 -->\n\n")
        note = note.replace("{{related_articles}}", "- 待补充相关文章")
        note = note.replace("{{further_reading}}", "- 待补充延伸阅读")
        note = note.replace("{{generation_time}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return note
    
    def process_url(self, url: str, title: str = "", author: str = "") -> Dict:
        """处理单个URL"""
        print(f"\n处理: {url}")
        
        # 检查是否已存在
        for article in self.index["articles"]:
            if article["url"] == url:
                print(f"  [已存在] {article['file_path']}")
                return {"status": "exists", "info": article}
        
        # 获取文章内容（这里使用模拟数据，实际应调用webfetch）
        # 实际使用时，需要手动输入或从其他方式获取
        article_info = {
            "url": url,
            "title": title or "待获取标题",
            "author": author or "Unknown",
            "publish_date": "",
            "category": "",
            "tags": [],
            "summary": "",
            "content": "",
            "code": ""
        }
        
        # 自动分类
        if self.config["auto_classify"]:
            article_info["category"] = self.auto_classify(
                article_info["title"], 
                article_info.get("content", "")
            )
        
        # 提取标签
        article_info["tags"] = self.extract_tags(
            article_info["title"],
            article_info.get("content", "")
        )
        
        return {"status": "processed", "info": article_info}
    
    def save_article(self, article_info: Dict) -> str:
        """保存文章为笔记"""
        # 确保title不为None
        title = article_info.get("title") or "Untitled"
        article_info["title"] = title
        
        # 确定保存路径
        category = article_info.get("category", "Others")
        category_path = self.config["categories"][category]["path"]
        
        # 创建目录
        os.makedirs(category_path, exist_ok=True)
        
        # 生成文件名
        filename = self.generate_filename(title)
        file_path = os.path.join(category_path, filename)
        
        # 创建图片目录
        images_dir = os.path.join(category_path, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # 处理内容中的图片
        content = article_info.get("content", "")
        if content:
            content, images = self.extract_images(content, images_dir, filename)
            content = self.replace_image_refs(content, images, category_path)
            article_info["content"] = content
            
            if images:
                print(f"    已下载 {len(images)} 张图片到 images/ 目录")
        
        # 创建笔记
        note_content = self.create_note(article_info)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        # 更新索引
        index_entry = {
            "title": article_info["title"],
            "url": article_info["url"],
            "author": article_info["author"],
            "category": category,
            "tags": article_info["tags"],
            "file_path": file_path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.index["articles"].append(index_entry)
        self.save_index()
        
        print(f"  已保存: {file_path}")
        return file_path
        """保存文章为笔记"""
        # 确保title不为None
        title = article_info.get("title") or "Untitled"
        article_info["title"] = title
        
        # 确定保存路径
        category = article_info.get("category", "Others")
        category_path = self.config["categories"][category]["path"]
        
        # 创建目录
        os.makedirs(category_path, exist_ok=True)
        
        # 生成文件名
        filename = self.generate_filename(title)
        file_path = os.path.join(category_path, filename)
        
        # 创建笔记
        note_content = self.create_note(article_info)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        # 更新索引
        index_entry = {
            "title": article_info["title"],
            "url": article_info["url"],
            "author": article_info["author"],
            "category": category,
            "tags": article_info["tags"],
            "file_path": file_path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.index["articles"].append(index_entry)
        self.save_index()
        
        print(f"  [已保存] {file_path}")
        return file_path
    
    def batch_process(self, urls: List[str], titles: Optional[List[str]] = None):
        """批量处理URL列表"""
        print("=" * 60)
        print("Article Saver - 批量处理")
        print("=" * 60)
        
        processed = 0
        skipped = 0
        failed = 0
        
        for i, url in enumerate(urls):
            if not url.strip():
                continue
            
            title = titles[i] if titles and i < len(titles) else ""
            
            try:
                result = self.process_url(url.strip(), title)
                
                if result["status"] == "exists":
                    skipped += 1
                else:
                    # 在实际使用中，这里需要手动输入文章内容
                    # 或从其他方式获取
                    print(f"  [需手动整理内容]")
                    processed += 1
                    
            except Exception as e:
                print(f"  [失败] {str(e)}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"处理完成: 成功 {processed}, 跳过 {skipped}, 失败 {failed}")
        print("=" * 60)
    
    def list_articles(self, category: Optional[str] = None):
        """列出所有文章"""
        print("\n" + "=" * 60)
        print("文章列表")
        print("=" * 60)
        
        articles = self.index["articles"]
        
        if category:
            articles = [a for a in articles if a["category"] == category]
        
        # 按分类分组
        by_category = {}
        for article in articles:
            cat = article["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        # 打印
        for cat, articles in sorted(by_category.items()):
            print(f"\n[{cat}] ({len(articles)}篇)")
            for article in articles:
                print(f"  - {article['title']}")
                print(f"    标签: {', '.join(article['tags'])}")
                print(f"    文件: {article['file_path']}")
    
    def search(self, keyword: str):
        """搜索文章"""
        print("\n" + "=" * 60)
        print(f"搜索: {keyword}")
        print("=" * 60)
        
        keyword_lower = keyword.lower()
        results = []
        
        for article in self.index["articles"]:
            if (keyword_lower in article["title"].lower() or
                keyword_lower in article["category"].lower() or
                any(keyword_lower in tag.lower() for tag in article["tags"])):
                results.append(article)
        
        if results:
            print(f"\n找到 {len(results)} 篇相关文章:")
            for article in results:
                print(f"\n  [文章] {article['title']}")
                print(f"     分类: {article['category']}")
                print(f"     标签: {', '.join(article['tags'])}")
                print(f"     文件: {article['file_path']}")
        else:
            print("\n未找到相关文章")
    
    def generate_stats(self):
        """生成统计报告"""
        print("\n" + "=" * 60)
        print("知识库统计")
        print("=" * 60)
        
        total = len(self.index["articles"])
        print(f"\n总文章数: {total}")
        
        # 分类统计
        by_category = {}
        for article in self.index["articles"]:
            cat = article["category"]
            by_category[cat] = by_category.get(cat, 0) + 1
        
        print("\n分类分布:")
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
            percentage = count / total * 100
            print(f"  {cat:15s}: {count:3d}篇 ({percentage:5.1f}%)")
        
        # 标签统计
        all_tags = []
        for article in self.index["articles"]:
            all_tags.extend(article["tags"])
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print("\n热门标签 (Top 10):")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {tag}: {count}次")


def main():
    """主函数"""
    saver = ArticleSaver()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python batch_processor.py process <urls.txt>    # 批量处理")
        print("  python batch_processor.py list [category]       # 列出文章")
        print("  python batch_processor.py search <keyword>      # 搜索文章")
        print("  python batch_processor.py stats                 # 统计信息")
        return
    
    command = sys.argv[1]
    
    if command == "process":
        if len(sys.argv) < 3:
            # 从命令行输入URL
            print("请输入文章URL（每行一个，输入空行结束）:")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                saver.batch_process(urls)
        else:
            # 从文件读取URL
            url_file = sys.argv[2]
            with open(url_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            saver.batch_process(urls)
    
    elif command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        saver.list_articles(category)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("请输入搜索关键词")
            return
        saver.search(sys.argv[2])
    
    elif command == "stats":
        saver.generate_stats()
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
