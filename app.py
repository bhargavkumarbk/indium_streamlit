import mmh3
import random
import streamlit as st
import pandas as pd
import pickle
# import pygsheets
import os
from warnings import filterwarnings
filterwarnings("ignore")

from datetime import datetime, timedelta
try:
    from github import Github
except Exception as e:
    st.write(e)
# import sys
# st.write(sys. version)

data = pd.read_csv('Streamlit_Response.csv')
exist_df=pd.DataFrame(data)

# exist_df.columns = exist_df.iloc[0]
# exist_df = exist_df[1:] 
exist_df = exist_df.reset_index(drop=True)

# loading passages and questionnaire

data = pd.read_csv('passage_questions.csv')
psg_qstn=pd.DataFrame(data)

# psg_qstn.columns = psg_qstn.iloc[0]
# psg_qstn = psg_qstn[1:] 
psg_qstn = psg_qstn.reset_index(drop=True)

data = pd.read_csv('passage_mcq_key.csv')
options_df=pd.DataFrame(data)

# options_df.columns = options_df.iloc[0]
# options_df = options_df[1:] 
options_df = options_df.reset_index(drop=True)

# list of questions
lst = ['PQ1', 'PQ2', 'PQ3', 'PQ4', 'PQ5', 'CQ1', 'CQ2', 'CQ3']

#creating a df to append new submission
# df = pd.DataFrame(columns=["Timestamp","Organisation", "Email Id","Set No.", "Summary", "Response", "PQ1","PQ2","PQ3","PQ4","PQ5","CQ1","CQ2","CQ3"])
df = exist_df.copy()
def append_to_df(selected_org,email_id,set_no, ticket_summary, ticket_response, mcq_answers):
    global df
    
    current_time = datetime.now()
    current_timestamp = (current_time+timedelta(hours=5, minutes=30)).strftime("%m/%d/%Y %X")
    new_data = {"Timestamp":current_timestamp,
                "Organisation":selected_org, 
                "Email Id":email_id, 
                "Set No.":set_no,
                "Summary":ticket_summary, 
                "Response":ticket_response, 
                "PQ1": mcq_answers[0],
                "PQ2": mcq_answers[1],
                "PQ3": mcq_answers[2],
                "PQ4": mcq_answers[3],
                "PQ5": mcq_answers[4],
                "CQ1": mcq_answers[5],
                "CQ2": mcq_answers[6],
                "CQ3": mcq_answers[7]}
    try:
        df.loc[len(df)] = new_data
        # df=df.append(new_data, ignore_index=True)
    except Exception as e: st.write(e)

def append_to_github_csv(df):
    # define parameters for a request
    token = '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' 
    owner = 'harikaa6'
    repo = 'streamlit-dashboard'
    path = 'Streamlit_Response.csv'
    commit_message = 'Update CSV file'
    github = Github(token)
    repo = github.get_user(owner).get_repo(repo)
    
    content = repo.get_contents(path)
    
    contents=bytes(df.to_csv(index=False), encoding='utf-8')
    repo.update_file(path, commit_message, contents, content.sha)

        


# Function to generate a random passage and questionnaire based on the selected organization
def generate_random_passage_and_questionnaire(org,i):

    
    result = psg_qstn[(psg_qstn['Org']==org ) & (psg_qstn['ID']==i )].reset_index(drop=True)

    if len(result)==0:
        return "You have attempted all the sets"
    else:
        return result

    
    
def randomisation(selected_org,email_id):
    

    setnos = psg_qstn[(psg_qstn['Org']==selected_org )]['ID'].to_list()
    
    
    # completed set nos byb each individual
    attempted_sets = exist_df[(exist_df['Organisation']==selected_org ) & ( exist_df['Email Id']==email_id)]['Set No.'].to_list()
    

    str_encode = email_id+selected_org
    # removing already attempted sets
    for i in set(attempted_sets):
        try:
            setnos.remove(i)
        except:
            continue
    try:
        hash_value = mmh3.hash(str_encode)
        n = len(setnos)
        ind = hash_value%n
        rq = setnos[ind]

#         st.write('hash',hash_value,'...n',n,'..ind',ind,'..rq',rq)
    except:
        rq=0

    return rq
    

def assessment_form():
    
    st.title("Assessment Form")

    # Section 0: Emailid
#     st.header("Enter your Emailid*")
    email_id = st.text_area("Enter your Email id*", max_chars=50)
    # Section 0: Organization Selection
    org_options = ["Select your Language"]  # Add more organizations as needed
    orgs = set(psg_qstn['Org'].to_list())
    orgs = list(orgs)
    org_options.extend(orgs)
    selected_org = st.selectbox("Select Language", org_options)
    

    # Display passages and questions only if an organization is selected
    if selected_org != "Select your Language" and email_id:
        # Generate a random passage and questionnaire based on the selected organization
        rq = randomisation(selected_org,email_id)
        st.write(rq)

        # Generate a random passage and questionnaire based on the selected organization
        random_passage_and_questionnaire = generate_random_passage_and_questionnaire(selected_org,rq)


        if isinstance(random_passage_and_questionnaire, str):
            st.markdown(f'<div style="color: black; background-color: #F0F0F0; padding: 10px">{random_passage_and_questionnaire}</div>',unsafe_allow_html=True)
            return
        
        # Display random passage
        st.markdown('<div style="color: black; background-color: #F0F0F0; padding: 10px">{passage}</div>'.format(passage=random_passage_and_questionnaire['Passage'][0]),unsafe_allow_html=True)
#        st.header(f"Passage: {random_passage_and_questionnaire[0]}")
#         st.text_area("Sample Ticket/Passage", value=random_passage_and_questionnaire[0], height=400, disabled=True)



        # Section 1: Summarise the passage
        st.header("1.Summarise the passage*")
        ticket_summary = st.text_area("Enter passage summary")

        # Section 2: Respond to the passage
        st.header("2.Respond to the passage*")
        ticket_response = st.text_area("Enter passage response")

        # Display random questionnaire
        user_responses = {}
        mcq_answers = []
        for i, question in enumerate(lst):
            tmp_options_df = options_df[(options_df['ID']==rq) & (options_df['Question']==question)]
            options = tmp_options_df.iloc[0][['OptionA','OptionB','OptionC','OptionD']].to_list()
            st.header(f"{i + 3}. {random_passage_and_questionnaire[question][0].strip()}*")
            user_response = st.radio("", options)
            user_responses[f"{i + 3}. {question[0]}"] = user_response
            mcq_answers.append(user_response)

        # Submit button
        if st.button("Submit"):
            # Validate that all mandatory fields are filled before submission
            if email_id and ticket_summary and ticket_response and all(response for response in user_responses.values()):
                # Customize the behavior upon successful submission (e.g., store data, process data)
                st.success("Form Submitted Successfully!")
                # You can add further processing steps here
                append_to_df(selected_org,email_id,rq,ticket_summary, ticket_response, mcq_answers)
                # df.to_csv('Streamlit_Response.csv',mode = 'a', index = False, header = False)
                append_to_github_csv(df)
#                 GSHEETS APPENDING  --- data = pull_sheet_data(SCOPES,SPREADSHEET_ID,'Streamlite Response!A:N')

#                 append_to_df(selected_org,email_id,rq,ticket_summary, ticket_response, mcq_answers)
#                 last_row = len(data)+1
#                 update_sheet_data(SPREADSHEET_ID,'Streamlite Response!A{row}:N'.format(row=last_row),df)

            else:
                st.warning("Please fill in all mandatory fields (*) before submitting.")
        # Display submitted information
#         st.subheader("Submitted Information:")
#         st.write(f"Selected Organization: {selected_org}")
#         st.write(f"Enter your Emailid: {email_id}")
#         st.write(f"1. Summarise the ticket: {ticket_summary}")
#         st.write(f"2. Respond to the ticket: {ticket_response}")
#         for question, response in user_responses.items():
#             st.write(f"{question}: {response}")

if __name__ == "__main__":
    assessment_form()
