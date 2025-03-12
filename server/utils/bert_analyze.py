from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
def analyze_text(sentences): 
     
    # 加载模型和分词器
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")
    sentence_embeddings = []
    for sentence in sentences: 
        inputs = tokenizer(sentence, return_tensors="pt")
        outputs = model(**inputs)
        sentence_embeddings.append(outputs.last_hidden_state.mean(dim=1)[0]) 
    # Convert torch tensors to numpy arrays
    sentence_embeddings_np = [embedding.detach().numpy() for embedding in sentence_embeddings]
    repeat_sentence_indices = []
    # Calculate cosine similarity between sentence embeddings
    similarities = cosine_similarity(sentence_embeddings_np, sentence_embeddings_np)
    for i in range(len(similarities)):
        if i in repeat_sentence_indices: continue
        for j in range(len(similarities[i])):
            if similarities[i][j]>0.9 and i!=j:
                repeat_sentence_indices.append(j) 
    # 通过倒序遍历删除元素，避免影响索引
    for i in sorted(repeat_sentence_indices, reverse=True):
        del sentences[i]
    return sentences
