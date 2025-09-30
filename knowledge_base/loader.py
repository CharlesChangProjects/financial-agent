from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredHTMLLoader,
    CSVLoader
)
from config.settings import Settings

def load_documents(file_path: str):
    """根据文件类型自动选择加载器"""
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".html"):
        loader = UnstructuredHTMLLoader(file_path)
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    return loader.load()

# 示例用法
if __name__ == "__main__":
    docs = load_documents(f"{Settings.DATA_DIR}/raw/reports/sample.pdf")
    print(f"Loaded {len(docs)} pages")