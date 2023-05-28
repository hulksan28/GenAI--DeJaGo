import os
from langchain import LLMChain, PromptTemplate, OpenAI

def prompt_generator(file, code):
    while True:
        question = input("Q: ")

        if question == 'N':
            break

        context = code
        response = get_llm_response(context, question)

        print(f'A: {response}')


def code_query(codebase_folder):
    for root, dirs, files in os.walk(codebase_folder):
        for file in files:
            if file.endswith(".py"):
                print(file)
                with open(os.path.join(root, file), 'r') as inp:
                    code = inp.read()
                    prompt_generator(file, code)


def get_llm_response(context, user_input):
    return chatbot.predict(context=context, input=user_input)

openai_api_key = "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"
llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
chat_summary_prompt = PromptTemplate(
    input_variables=["context", "input"],
    template="""
    Given the following code for the methods in the codebase, please answer this question "{input}"?  Let's also work this out in a step by step in way to be sure we have the right answer
    Summary of methods: 
    {context} Let's also work this out in a step by step in way to be sure we have the right answer"""
)

#prompt = "Provide the answer to the query based on the below-mentioned method:\n"
chatbot = LLMChain(
    llm=llm,
    prompt=chat_summary_prompt,
    verbose=True,
)

code_query('D:/hulk/Projects/chat-twitter/')