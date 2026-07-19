from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag.retrieve import retrieve
from services.llm_service import get_llm

llm=get_llm()

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are an AI assistant.

Answer ONLY from the supplied context.

Rules:

- Never hallucinate.
- If the answer isn't found, reply:
  I don't know.
- Mention filename and page number whenever possible.
- Keep answers concise.

Context:
{context}
"""
),
("human", "{question}")
]
)

chain = prompt | llm | StrOutputParser()

def ask_question(question):

    documents = retrieve(question)
    if not documents:
       return (
           "I don't know. No relevant information was found in the uploaded documents.",
           []
       )

    context_parts = []
    for doc in documents:
        context_parts.append(
             f"""
    Source: {doc['filename']}
    Page: {doc['page']}

    Content:
    {doc['text']}
    """
       )
    context = "\n\n".join(context_parts)

    response = chain.invoke(
        {
            "context": context,
            "question": question
        }
    )
    return response, documents