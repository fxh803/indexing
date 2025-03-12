# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
client = OpenAI(api_key="sk-7907fe173aef4c74ad3c9b92107d38dd", base_url="https://api.deepseek.com")
def ask_deepseek_about_contextual_words(question):
   
    system_prompt = """
        The user will provide some keywords and sentences. 
        Please find out "contextual words" related to "keyword" in sentences and output them in JSON format. 

        EXAMPLE INPUT: 
        sentences = "The study explores the relationship between climate change, deforestation, and biodiversity loss. It highlights how rising temperatures exacerbate deforestation, which in turn accelerates biodiversity loss. The paper also discusses potential mitigation strategies, such as reforestation and sustainable land management."  
        keywords = ["climate change"]

        EXAMPLE JSON OUTPUT:{
            "edges":[{
                "keyword": "climate change",
                "contextual word": "deforestation",
                "label": "exacerbates",
                "evidence": "It highlights how rising temperatures exacerbate deforestation."
            }]
        }
        
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt },
            {"role": "user", "content": question },
        ],  
        response_format={
        'type': 'json_object'
        }
    )
    return response.choices[0].message.content

def ask_deepseek_about_knowledgeGraph(question):
   
    system_prompt = """
        The user will provide fulltext of a paper and some keywords in this paper.
        Please build a knowledge graph about keywords and output them in JSON format. 

        EXAMPLE INPUT: 
        article = "The study explores the relationship between climate change, deforestation, and biodiversity loss. It highlights how rising temperatures exacerbate deforestation, which in turn accelerates biodiversity loss. The paper also discusses potential mitigation strategies, such as reforestation and sustainable land management."  
        keywords = ["climate change", "deforestation", "biodiversity loss", "reforestation", "sustainable land management"]  
        "Based on this article, construct a knowledge graph of these keywords." 

        EXAMPLE JSON OUTPUT:
        {
        "nodes": [
            {"id": "0", "label": "Climate Change"},
            {"id": "1", "label": "Deforestation"},
            {"id": "2", "label": "Biodiversity Loss"},
            {"id": "3", "label": "Reforestation"},
            {"id": "4", "label": "Sustainable Land Management"}
        ],
        "edges": [
            {
            "source": "climate change",
            "target": "deforestation",
            "source_id": "0",
            "target_id": "1",
            "label": "exacerbates",
            "evidence": "It highlights how rising temperatures exacerbate deforestation."
            },
            {
            "source": "deforestation",
            "target": "biodiversity loss",
            "source_id": "1",
            "target_id": "2",
            "label": "accelerates",
            "evidence": "Deforestation, in turn, accelerates biodiversity loss."
            },
            {
            "source": "reforestation",
            "target": "biodiversity loss",
            "source_id": "3",
            "target_id": "2",
            "label": "mitigates",
            "evidence": "The paper discusses potential mitigation strategies, such as reforestation."
            },
            {
            "source": "sustainable land management",
            "target": "deforestation",
            "source_id": "4",
            "target_id": "1",
            "label": "reduces",
            "evidence": "Sustainable land management is discussed as a strategy to reduce deforestation."
            }
        ]
        }
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt },
            {"role": "user", "content": question },
        ],  
        response_format={
        'type': 'json_object'
        }
    )
    return response.choices[0].message.content
 