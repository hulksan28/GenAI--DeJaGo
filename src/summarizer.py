import ast
import os
from langchain import LLMChain, PromptTemplate, OpenAI
# from langchain.memory import ConversationBufferMemory
import chromadb


class Summarizer:
    def __init__(self, codebase_folder, summary_file, prompt, openai_api_key, collection_name):
        self.codebase_folder = codebase_folder
        self.summary_file = summary_file
        self.prompt = prompt
        self.llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        self.summaries = ''

    def get_summary(self):
        for root, dirs, files in os.walk(self.codebase_folder):
            for file in files:
                if file.endswith(".py"): #and file.startswith("summarizer") is False:
                    #print(f'Processing file {file}...')

                    with open(os.path.join(root, file), 'r') as inp:
                        code = inp.read()
                        tree = ast.parse(code)
                        self.walk_tree(code, tree)

                    #print(f'Finished processing file {file}.')

        self.write_summary()

    def walk_tree(self, code, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('__') is False:
                self.summaries += f'{self.summarize_method(code, node)}\n-----\n'

    def summarize_method(self, code, node):
        #print(f'Summarizing method {node.name}...')
        start_line = node.lineno
        end_line = node.body[-1].lineno
        method_lines = code.split('\n')[start_line-1:end_line]
        #print('method_lines')
        
        method_source = '\n'.join(method_lines)
        #print(method_source)
        llm_output = self.llm(self.prompt + method_source).strip()
        method_summary = ": ".join([node.name, llm_output.strip()])

        #print(f'Finished summarizing method {node.name}.')
        return method_summary

    def write_summary(self):
        with open(self.summary_file, 'w') as out:
            out.write(self.summaries)


class Embeddings:
    def __init__(self, summary_file, collection_name):
        self.summary_file = summary_file
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(collection_name)

    def create_embeddings(self):
        with open(self.summary_file, 'r') as f:
            file_content = f.read().split('-----')

            for line in file_content:
                line = line.strip()
                method_name = line.split(':')[0]

                self.collection.add(
                    documents = [line], 
                    metadatas = [{"source": method_name}], 
                    ids = method_name
                )

    def query_collection(self, query, k):
        return self.collection.query(
            query_texts=[query],
            n_results=k)
        


class ChatBot:
    def __init__(self, embeddings, prompt, openai_api_key):
        self.embeddings = embeddings
        self.llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        self.prompt = prompt
        self.chatbot = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True,
        )

    def simulate_chat(self):
        print('Welcome to Talk to Codebase! Press N to exit...')

        while True:
            question = input("Q: ")

            if question == 'N':
                break

            relevant_docs = self.embeddings.query_collection(question, 2)
            context = "\n".join(relevant_docs['documents'][0])
            response = self.get_llm_response(context, question)

            print(f'A: {response}')


    def get_llm_response(self, context, input):
        return self.chatbot.predict(context=context, input=input)


if __name__ == "__main__":
    codebase_folder = "."
    summary_file = "summary.txt"
    method_summary_prompt = "Provide a summary of what the below mentioned method does:\n"
    openai_api_key = "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"
    collection_name = "code_summary"
    summarizer = Summarizer(
        codebase_folder, summary_file, method_summary_prompt, openai_api_key, collection_name)
    summarizer.get_summary()

    embeddings = Embeddings(summary_file, collection_name)
    embeddings.create_embeddings()
    
    chat_template = """
    Given the following summary for the methods in the codebase, please answer this question "{input}"?  Let's also work this out in a step by step in way to be sure we have the right answer
    Summary of methods: 
    {context}

    
    """
    chat_summary_prompt = PromptTemplate(
        input_variables=["context", "input"],
        template=chat_template)
    chatbot = ChatBot(embeddings, chat_summary_prompt, openai_api_key)
    chatbot.simulate_chat()
