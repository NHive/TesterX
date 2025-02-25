import json
import os
import uuid
import datetime
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import shutil
import faiss
from testerx.agent.embedding import EmbeddingModel


class JsonDataAccess:
    """基于JSON文件和Faiss的数据访问类，优化向量搜索，自动生成和使用 Embedding"""

    def __init__(self, data_dir: str = "res/memory_data", embedding_dimension: int = 1536):
        """
        初始化数据访问层，并加载Faiss索引, 初始化 EmbeddingModel

        Args:
            data_dir: 存储JSON文件的目录
            embedding_dimension: 嵌入向量的维度
        """
        self.data_dir = data_dir
        self.memories_dir = os.path.join(data_dir, "memories")
        self.embeddings_dir = os.path.join(data_dir, "embeddings")
        self.tags_file = os.path.join(data_dir, "tags.json")
        self.embedding_dimension = embedding_dimension
        self._ensure_directories()
        self._load_tags()

        self.faiss_index = None
        self.memory_ids_indexed = []  # 存储索引中memory_id的顺序
        self._build_faiss_index()

        # 初始化 EmbeddingModel
        self.embedding_model_client = EmbeddingModel()

    def _ensure_directories(self):
        """确保所需的目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.memories_dir, exist_ok=True)
        os.makedirs(self.embeddings_dir, exist_ok=True)

        # 初始化tags文件如果不存在
        if not os.path.exists(self.tags_file):
            with open(self.tags_file, 'w') as f:
                json.dump([], f)

    def _load_tags(self):
        """加载所有标签"""
        try:
            with open(self.tags_file, 'r') as f:
                self.tags = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.tags = []
            self._save_tags()

    def _save_tags(self):
        """保存标签列表"""
        with open(self.tags_file, 'w') as f:
            json.dump(self.tags, f)

    def _add_tags(self, tag_names: List[str]) -> List[str]:
        """
        添加标签，如果不存在则创建

        Returns:
            添加的标签名列表
        """
        for tag_name in tag_names:
            if tag_name not in self.tags:
                self.tags.append(tag_name)
        self._save_tags()
        return tag_names

    def _get_memory_file_path(self, memory_id: str) -> str:
        """获取记忆JSON文件路径"""
        return os.path.join(self.memories_dir, f"{memory_id}.json")

    def _get_embedding_file_path(self, memory_id: str) -> str:
        """获取嵌入向量文件路径"""
        return os.path.join(self.embeddings_dir, f"{memory_id}.npy")

    def _save_embedding(self, memory_id: str, embedding: np.ndarray):
        """保存嵌入向量到文件, 并更新Faiss索引"""
        np.save(self._get_embedding_file_path(memory_id), embedding)
        self._update_faiss_index_single(memory_id, embedding)

    def _load_embedding(self, memory_id: str) -> Optional[np.ndarray]:
        """从文件加载嵌入向量"""
        path = self._get_embedding_file_path(memory_id)
        if os.path.exists(path):
            return np.load(path)
        return None

    def _save_memory(self, memory_data: Dict[str, Any]):
        """保存记忆数据到JSON文件"""
        file_path = self._get_memory_file_path(memory_data['id'])
        with open(file_path, 'w') as f:
            # 深拷贝以避免修改原始数据
            data_to_save = memory_data.copy()
            # 移除embedding字段，因为它被Faiss索引管理
            if 'embedding' in data_to_save:
                del data_to_save['embedding']
            json.dump(data_to_save, f, indent=2)

    def _load_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """从JSON文件加载记忆数据，不包含embedding，embedding由Faiss管理"""
        file_path = self._get_memory_file_path(memory_id)
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            memory_data = json.load(f)
            return memory_data

    def _get_all_memory_ids(self) -> List[str]:
        """获取所有记忆的ID列表"""
        memory_files = [f for f in os.listdir(self.memories_dir) if f.endswith('.json')]
        return [os.path.splitext(f)[0] for f in memory_files]

    def _format_memory_data(self, content: str, content_type: str,
                            tags: List[str] = None,
                            metadata: Dict[str, Any] = None,
                            importance: float = 1.0) -> Dict[str, Any]:
        """格式化记忆数据"""
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}

        return {
            'id': str(uuid.uuid4()),
            'content': content,
            'content_type': content_type,
            'tags': tags,
            'metadata': metadata,
            'importance': importance,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }

    def _build_faiss_index(self):
        """构建或重新构建Faiss索引"""
        memory_ids = self._get_all_memory_ids()
        embeddings_list = []
        indexed_memory_ids = []

        for memory_id in memory_ids:
            embedding = self._load_embedding(memory_id)
            if embedding is not None:
                embeddings_list.append(embedding)
                indexed_memory_ids.append(memory_id)

        if embeddings_list:
            embeddings_array = np.array(embeddings_list, dtype=np.float32)
            self.faiss_index = faiss.IndexFlatL2(self.embedding_dimension)  # 使用 IndexFlatL2 索引
            self.faiss_index.add(embeddings_array)
            self.memory_ids_indexed = indexed_memory_ids
        else:
            self.faiss_index = faiss.IndexFlatL2(self.embedding_dimension)  # 创建一个空的索引
            self.memory_ids_indexed = []

    def _update_faiss_index_single(self, memory_id: str, embedding: np.ndarray):
        """更新Faiss索引中的单个向量 (简化版本，更高效的更新需要更复杂的索引管理)"""
        self._build_faiss_index()  # 简单起见，每次更新都重建索引。

    # ========== 基本CRUD操作 ==========
    def add_memory(self,
                   content: str,
                   content_type: str,
                   metadata: Dict[str, Any] = None,
                   tags: List[str] = None,
                   importance: float = 1.0) -> Dict[str, Any]:
        """
        添加新的记忆, 自动生成 embedding 向量

        Args:
            content: 记忆内容
            content_type: 内容类型
            metadata: 元数据字典
            tags: 标签列表
            importance: 重要性/优先级

        Returns:
            创建的Memory对象
        """
        # 创建基本记忆数据
        memory_data = self._format_memory_data(
            content=content,
            content_type=content_type,
            tags=tags or [],
            metadata=metadata or {},
            importance=importance
        )

        # 添加标签
        if tags:
            self._add_tags(tags)

        # 生成 embedding 向量
        embedding_vector = self.embedding_model_client.get_embedding(content)
        embedding_np = np.array(embedding_vector, dtype=np.float32)

        # 保存记忆数据 (不包含embedding)
        self._save_memory(memory_data)

        # 保存嵌入向量并更新Faiss索引
        self._save_embedding(memory_data['id'], embedding_np)

        # 加载完整数据（不包括嵌入向量，因为Faiss管理embedding）并返回
        return self._load_memory(memory_data['id'])

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """通过ID获取记忆"""
        return self._load_memory(memory_id)

    def update_memory(self, memory_id: str, content: str = None, embedding: np.ndarray = None, **kwargs) -> bool:
        """更新记忆，可以同时更新内容、元数据和embedding"""
        memory_data = self._load_memory(memory_id)
        if not memory_data:
            return False

        # 更新提供的字段
        for key, value in kwargs.items():
            if key == 'tags' and isinstance(value, list):
                # 更新标签
                memory_data['tags'] = value
                self._add_tags(value)
            elif key in memory_data:
                memory_data[key] = value

        if content:
            memory_data['content'] = content

            # 重新生成 embedding 向量
            embedding_vector = self.embedding_model_client.get_embedding(content)
            embedding_np = np.array(embedding_vector, dtype=np.float32)
            embedding = embedding_np  # 使用新生成的 embedding 更新

        # 更新时间戳
        memory_data['updated_at'] = datetime.datetime.now().isoformat()

        # 保存更新后的记忆 (不包含embedding)
        self._save_memory(memory_data)

        # 如果提供了新的embedding 或 新内容导致embedding更新，则更新
        if embedding is not None and isinstance(embedding, np.ndarray):
            self._save_embedding(memory_id, embedding)

        return True

    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆，并重建Faiss索引"""
        memory_file = self._get_memory_file_path(memory_id)
        embedding_file = self._get_embedding_file_path(memory_id)

        success = True

        if os.path.exists(memory_file):
            try:
                os.remove(memory_file)
            except OSError:
                success = False

        if os.path.exists(embedding_file):
            try:
                os.remove(embedding_file)
            except OSError:
                success = False

        if success:
            self._build_faiss_index()  # 删除后需要重建索引
        return success

    # ========== 向量检索 ==========
    def find_similar_memories(self,
                              query_embedding: np.ndarray,
                              content_type: Optional[str] = None,
                              tags: Optional[List[str]] = None,
                              top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        使用Faiss通过向量相似度查找相似记忆

        Args:
            query_embedding: 查询向量 (numpy 数组)
            content_type: 可选的内容类型过滤
            tags: 可选的标签过滤
            top_k: 返回的最大结果数

        Returns:
            (Memory, similarity_score) 元组的列表，按相似度降序排序
        """
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []  # 如果索引为空，则返回空列表

        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)  # 确保数据类型和形状正确
        D, I = self.faiss_index.search(query_embedding, top_k)  # 使用Faiss搜索

        results = []
        for i, index in enumerate(I[0]):
            if index != -1 and index < len(self.memory_ids_indexed):  # 检查索引是否有效
                memory_id = self.memory_ids_indexed[index]
                memory_data = self._load_memory(memory_id)

                # 应用过滤条件 (在Faiss检索后再次过滤)
                if content_type and memory_data.get('content_type') != content_type:
                    continue
                if tags and not all(tag in memory_data.get('tags', []) for tag in tags):
                    continue

                similarity_score = 1.0 - (D[0][i] / 2.0) if D[0][i] <= 2.0 else 0.0  # 将L2距离转换为粗略的相似度评分 (根据实际情况调整)
                results.append((memory_data, float(similarity_score)))

        # 确保结果数量不超过top_k，并按相似度降序排序 (Faiss已经按距离排序，这里可以简化)
        results.sort(key=lambda x: x[1], reverse=True)  # 显式按相似度排序, 虽然L2距离排序通常足够
        return results[:top_k]

    def search_memories(self,
                        query_text: str,
                        content_type: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        使用 EmbeddingModel 生成查询向量并搜索相似记忆

        Args:
            query_text: 查询文本
            content_type: 可选的内容类型过滤
            tags: 可选的标签过滤
            top_k: 返回的最大结果数

        Returns:
            (Memory, similarity_score) 元组的列表，按相似度降序排序
        """
        # 获取查询文本的 embedding 向量
        query_embedding_vector = self.embedding_model_client.get_embedding(query_text)
        query_embedding_np = np.array(query_embedding_vector, dtype=np.float32)

        # 使用 embedding 向量进行搜索
        return self.find_similar_memories(
            query_embedding=query_embedding_np,
            content_type=content_type,
            tags=tags,
            top_k=top_k
        )

    # ========== 专门的API文档记忆操作 ==========
    # ... (以下API文档和测试用例记忆操作方法需要修改，移除 embedding 参数，并调用 self.add_memory)
    def add_api_doc_memory(self,
                           content: str,
                           api_path: str,
                           method: str,
                           summary: str = None,
                           description: str = None,
                           request_example: str = None,
                           response_example: str = None,
                           metadata: Dict[str, Any] = None,
                           tags: List[str] = None,
                           importance: float = 1.0) -> Dict[str, Any]:
        """添加API文档记忆, 自动生成 embedding"""
        # 合并元数据
        combined_metadata = {
            'api_path': api_path,
            'method': method,
            'summary': summary,
            'description': description,
            'request_example': request_example,
            'response_example': response_example
        }

        if metadata:
            combined_metadata.update(metadata)

        # 确保包含api标签
        combined_tags = tags or []
        if 'api' not in combined_tags:
            combined_tags.append('api')

        # 添加记忆，embedding 会在 add_memory 内部自动生成
        return self.add_memory(
            content=content,
            content_type='api_doc',
            metadata=combined_metadata,
            tags=combined_tags,
            importance=importance
        )

    def get_api_doc_by_path_method(self, api_path: str, method: str) -> Optional[Dict[str, Any]]:
        """通过路径和方法获取API文档记忆"""
        # 获取所有记忆
        memory_ids = self._get_all_memory_ids()

        for memory_id in memory_ids:
            memory_data = self._load_memory(memory_id)

            # 检查是否为API文档且匹配路径和方法
            if (memory_data.get('content_type') == 'api_doc' and
                    memory_data.get('metadata', {}).get('api_path') == api_path and
                    memory_data.get('metadata', {}).get('method') == method):
                return memory_data

        return None

    # ========== 专门的测试用例记忆操作 ==========
    def add_test_case_memory(self,
                             content: str,
                             test_name: str,
                             test_type: str,
                             test_script: str,
                             api_doc_id: str = None,
                             metadata: Dict[str, Any] = None,
                             tags: List[str] = None,
                             importance: float = 1.0) -> Dict[str, Any]:
        """添加测试用例记忆, 自动生成 embedding"""
        # 合并元数据
        combined_metadata = {
            'test_name': test_name,
            'test_type': test_type,
            'test_script': test_script,
            'api_doc_id': api_doc_id
        }

        if metadata:
            combined_metadata.update(metadata)

        # 确保包含test标签
        combined_tags = tags or []
        if 'test' not in combined_tags:
            combined_tags.append('test')

        # 添加记忆，embedding 会在 add_memory 内部自动生成
        return self.add_memory(
            content=content,
            content_type='test_case',
            metadata=combined_metadata,
            tags=combined_tags,
            importance=importance
        )

    def get_test_cases_for_api(self, api_doc_id: str) -> List[Dict[str, Any]]:
        """获取与特定API相关的所有测试用例"""
        # 获取所有记忆
        memory_ids = self._get_all_memory_ids()
        results = []

        for memory_id in memory_ids:
            memory_data = self._load_memory(memory_id)

            # 检查是否为测试用例且关联到指定API
            if (memory_data.get('content_type') == 'test_case' and
                    memory_data.get('metadata', {}).get('api_doc_id') == api_doc_id):
                results.append(memory_data)

        return results

    # ========== 对话记忆操作 ==========
    def add_conversation_memory(self,
                                role: str,
                                message: str,
                                metadata: Dict[str, Any] = None,
                                tags: List[str] = None,
                                importance: float = 1.0) -> Dict[str, Any]:
        """添加对话记忆, 自动生成 embedding"""
        # 合并元数据
        combined_metadata = {
            'role': role,
            'message': message
        }

        if metadata:
            combined_metadata.update(metadata)

        # 确保包含conversation标签
        combined_tags = tags or []
        if 'conversation' not in combined_tags:
            combined_tags.append('conversation')

        # 添加记忆，embedding 会在 add_memory 内部自动生成
        return self.add_memory(
            content=message,
            content_type='conversation',
            metadata=combined_metadata,
            tags=combined_tags,
            importance=importance
        )

    # ========== 批量操作 ==========
    def get_all_memories_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的所有记忆"""
        # 获取所有记忆
        memory_ids = self._get_all_memory_ids()
        results = []

        for memory_id in memory_ids:
            memory_data = self._load_memory(memory_id)

            # 检查内容类型
            if memory_data.get('content_type') == content_type:
                results.append(memory_data)

        return results

    def get_memories_by_tags(self, tags: List[str], require_all: bool = False) -> List[Dict[str, Any]]:
        """
        通过标签获取记忆

        Args:
            tags: 标签列表
            require_all: 如果为True，则只返回包含所有指定标签的记忆
        """
        # 获取所有记忆
        memory_ids = self._get_all_memory_ids()
        results = []

        for memory_id in memory_ids:
            memory_data = self._load_memory(memory_id)
            memory_tags = memory_data.get('tags', [])

            if require_all:
                # 要求包含所有标签
                if all(tag in memory_tags for tag in tags):
                    results.append(memory_data)
            else:
                # 包含任一标签即可
                if any(tag in memory_tags for tag in tags):
                    results.append(memory_data)

        return results

    def export_to_csv(self, output_path: str, content_type: str = None):
        """
        将记忆导出为CSV格式

        Args:
            output_path: 输出CSV文件路径
            content_type: 可选的内容类型过滤
        """
        import csv

        # 获取所有记忆
        memory_ids = self._get_all_memory_ids()
        memories = []

        for memory_id in memory_ids:
            memory_data = self._load_memory(memory_id)
            # 应用内容类型过滤
            if content_type and memory_data.get('content_type') != content_type:
                continue
            # 从内存中移除大型嵌入向量，CSV不导出embedding
            memories.append(memory_data)

        if not memories:
            return

        # 确定CSV字段
        # 获取所有可能的字段
        all_fields = set()
        for memory in memories:
            for key in memory.keys():
                all_fields.add(key)

        # 将metadata字段扁平化
        metadata_fields = set()
        for memory in memories:
            if 'metadata' in memory and isinstance(memory['metadata'], dict):
                for key in memory['metadata'].keys():
                    metadata_fields.add(f"metadata_{key}")

        # 组合所有字段
        fields = sorted(list(all_fields - {'metadata'})) + sorted(list(metadata_fields))

        # 写入CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for memory in memories:
                row = {k: v for k, v in memory.items() if k != 'metadata'}

                # 处理标签列表
                if 'tags' in row and isinstance(row['tags'], list):
                    row['tags'] = ','.join(row['tags'])

                # 扁平化metadata
                if 'metadata' in memory and isinstance(memory['metadata'], dict):
                    for k, v in memory['metadata'].items():
                        row[f"metadata_{k}"] = v

                writer.writerow(row)

    def backup(self, backup_dir: str):
        """
        备份所有记忆数据

        Args:
            backup_dir: 备份目录
        """
        os.makedirs(backup_dir, exist_ok=True)

        # 复制目录
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_dir = os.path.join(backup_dir, f"memory_backup_{timestamp}")

        shutil.copytree(self.data_dir, dest_dir)
        return dest_dir

    def clear_all_data(self):
        """清除所有数据（危险操作），并重建Faiss索引"""
        # 清除目录
        shutil.rmtree(self.memories_dir)
        shutil.rmtree(self.embeddings_dir)
        os.remove(self.tags_file)

        # 重新创建目录结构
        self._ensure_directories()
        self._load_tags()
        self._build_faiss_index()  # 清除数据后需要重建索引
        return True


if __name__ == '__main__':
    # 初始化数据访问层, 指定embedding维度
    data_access = JsonDataAccess("res/api_doc_memory_data", embedding_dimension=1536)

    # # 添加API文档记忆，无需传递 embedding 参数
    # memory = data_access.add_api_doc_memory(
    #     content="POST /api/v1/users 接口文档，创建新用户",  # 更换为 POST 请求
    #     api_path="/api/v1/users",
    #     method="POST",  # 更换为 POST 请求
    #     summary="创建新用户",  # 更新 summary
    #     tags=["api", "user", "create"]  # 添加 create 标签
    # )
    # print("添加的记忆:", memory)

    # 查找相似记忆，使用 search_memories 方法，自动生成查询 embedding
    query_text = "如何创建一个用户"  # 更换查询文本
    similar_memories = data_access.search_memories(
        query_text=query_text,
        content_type="api_doc",
        top_k=3
    )

    print("\n相似记忆 (EmbeddingModel 自动生成 embedding 并使用 Faiss 加速搜索):")
    for mem, score in similar_memories:
        print(f"Memory ID: {mem['id']}, Content: {mem['content']}, Similarity: {score:.4f}")
