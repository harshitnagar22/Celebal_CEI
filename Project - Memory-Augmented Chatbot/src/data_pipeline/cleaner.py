import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.config import config

class DataCleaner:
    def __init__(self, raw_dir=None, processed_dir=None):
        self.raw_dir = raw_dir or os.path.join(config.DATA_DIR, "raw")
        self.processed_dir = processed_dir or os.path.join(config.DATA_DIR, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def load_and_clean_data(self):
        """Loads JSON files from raw dir and cleans/chunks the text."""
        all_chunks = []
        
        if not os.path.exists(self.raw_dir):
            print(f"Directory {self.raw_dir} does not exist.")
            return all_chunks
            
        for filename in os.listdir(self.raw_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.raw_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                title = data.get("title", "")
                content = data.get("content", "")
                url = data.get("url", "")
                
                # Basic cleaning
                content = content.replace('\xa0', ' ')
                
                # Chunking
                chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(chunks):
                    all_chunks.append({
                        "id": f"{title}_chunk_{i}",
                        "text": chunk,
                        "metadata": {
                            "source": url,
                            "title": title,
                            "chunk_id": i
                        }
                    })
                    
        # Save chunks
        output_file = os.path.join(self.processed_dir, "chunks.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=4)
            
        print(f"Processed {len(all_chunks)} chunks and saved to {output_file}")
        return all_chunks

if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.load_and_clean_data()
