from typing import Set
import numpy as np
from backend.core import Shan_Story_LLM_Core 
from backend.relation_update import calculate_rank_difference

import streamlit as st
from streamlit_chat import message
from backend.helper import person_list, Relation_dict, Person_dict, question_extract
from backend.core import respond_list_0, respond_list_score_0

import os
#from config import OPENAI_API_KEY
#os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

story_llm_obj = Shan_Story_LLM_Core()
run_llm_selection_chain = story_llm_obj.run_llm_selection_chain
run_llm_end_story_chain = story_llm_obj.run_llm_end_story_chain
run_llm_nextday_story_chain = story_llm_obj.run_llm_nextday_story_chain

#Asking for OPENAI_API_KEY
text_input_container = st.empty()
t = text_input_container.text_input("Enter Your OPENAI_API_KEY")

if t != "":
    text_input_container.empty()
    os.environ["OPENAI_API_KEY"] = t
    story_llm_obj.iniciate_llm()
    
st.header("Story of Shan")

generated_response = None

if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []

if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = [
        f""" During my sophomore summer break, I found myself working at a coffee shop. As the clock struck three in the afternoon, the cozy ambiance was just beginning to fill with couples enjoying their coffee and sweet moments together.
        Suddenly, a guy with a skateboard appeared right in front of me. He had a mane of curly brown hair and deep, captivating eyes. His handsome features seemed even more alluring as he wiped his face, glistening with sweat. He said, "Give me an Americano, please." Then, with a surprised grin, he exclaimed, "Isn't this Shan? This is Jake! We took an economics class together!"
        """
    ]

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "selection" not in st.session_state:
    st.session_state["selection"] = '<select>'

if "selection_index" not in st.session_state:
    st.session_state["selection_index"] = None

if "selection_list" not in st.session_state:
    st.session_state["selection_list"] = []

if "options" not in st.session_state:
    st.session_state["options"] = None

def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string

selection = None
selection_index = None
#Show begining of the stories
message(st.session_state["chat_answers_history"][0], key = "bot_story0")


def generate_llm_options(chat_history, selection_index):
    
    if len(st.session_state["chat_history"]) == 0:
        character = "Jake"
    else:
        character = np.random.choice(person_list)

    print("selection index input", selection_index)


    if len(st.session_state["user_prompt_history"])%5==3:
        generated_response = run_llm_end_story_chain(chat_history, selection_index, character, Person_dict)
    elif len(st.session_state["user_prompt_history"])%5==4:
        generated_response = run_llm_nextday_story_chain(chat_history, selection_index, character, Person_dict)
    else:
        generated_response = run_llm_selection_chain(chat_history, selection_index, character, Person_dict)

    return character, generated_response

#side bar selection

#hi = len(st.session_state["user_prompt_history"])
hi = 0
showed_options = ['<select>', 'option1', 'option2', 'option3', 'option4']
selection = st.sidebar.selectbox('Select an action', showed_options,
                                key = "selection_box{}".format(hi+1))


#selection = orginal_options[selection_index]
print("selection", selection)
print('<select>'==selection)
print("selection list", st.session_state["selection_list"])

# display initial options
if len(st.session_state["chat_answers_history"])==1:

    options = ['<select>'] +   respond_list_0
    for opi in ["option{}: ".format(oi+1)+op for oi, op in enumerate(options)  if len(op)>0]:
        opi

if selection != '<select>':
    print("selection index", selection_index)
    st.session_state["selection"] ==  selection
    st.session_state["selection_index"] == showed_options.index(selection)-1


print("selection before entering spinner", st.session_state["selection"],
        st.session_state["options"], selection_index, st.session_state["selection_index"])


if selection != '<select>':
#if selection_index != None:
    with st.spinner("Generating response.."):

        selection_index = showed_options.index(selection)-1

        chat_history = st.session_state["chat_history"][1:]
        if selection_index == None:
            character, generated_response = generate_llm_options(chat_history, st.session_state["selection_index"])
        else:
            character, generated_response = generate_llm_options(chat_history, selection_index)

        formatted_response = (
            f"{generated_response['new_story']}"
        )

        print(generated_response['human_input'])
        
        outputed_input = generated_response['human_input'].split("Shan have decided to responded: ")
        if len(outputed_input)>1:
            outputed_input = outputed_input[1]
        else:
            outputed_input = "Continue the story"
        
        formatted_human_input = (
            f"{ outputed_input}"
        )
        
        st.session_state["user_prompt_history"].append(formatted_human_input)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(generated_response)

        i=1
        for user_query, response in zip(
            st.session_state["user_prompt_history"][:] ,
            st.session_state["chat_answers_history"][1:]
        ):
            i+=1
            message(user_query, is_user=True, key = "user_continue{}".format(i))
            message(response, key = "bot_story_continue{}".format(i))


        if generated_response.get("questions")!=None:
            options = question_extract(generated_response)
            options = [op for op in options if len(op)>0]
            orginal_options = list(options)
            options =['<select>'] +  ["option{}: ".format(oi)+op for oi, op in enumerate(options)  if len(op)>0]
        else:
            options = ['<select>', "Continue the story"]
            orginal_options = list(options)

        if len(options) == 2:
            option_show = ['<select>', "Continue the story"]
        else:
            option_show = ['<select>',"option1","option2","option3","option4"]

        for opi in options:
            f"{ opi}"
        
        st.session_state["options"] = option_show
        print("options -1 ", st.session_state["options"])
