from langchain_openai import ChatOpenAI
import json
import os
import pprint
os.environ["OPENAI_API_KEY"] = "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"

def proompting (data, job_desc):
    print(data)
    print(job_desc)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    IndustryExperience_str = str(data['industry_experience'])
    ResearchExperience_str = str(data['research_experience'])
    Projects_str = str(data['projects'])

    # llm = ChatOpenAI(model_name = "gpt-3.5-turbo-1106", temperature = 0)
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name = "gpt-4", temperature = 0)

    recommendations_prompt = (
        "Step 1) Consider the user's industry experience, research experience, and projects: "
        + "Industry Experience: " + IndustryExperience_str + "\n"
        + "Research Experience: " + ResearchExperience_str + "\n"
        + "Projects: " + Projects_str + "\n"
        + "Step 2) Consider the following job description: "
        + job_desc + "\n"
        + """
        Step 3) 
        What are the best industry experiences, research experiences, and projects to put on a resume for this job?
        Format your output VERY particularly, as follows: on the first line include the indices of the best industry 
        experiences, on the second line the indices of the best research projects, and on the third line the best
        projects for this job. Each line MUST HAVE BETWEEN 1 and 2 indices. 
        
        Do NOT say anything else other than the three lines of comma delimeted numbers. Do not give any affirmation
        of understanding my request or anything else, be completely silent except these lines of numbers.

        Example output:
        0
        1, 2
        5
        """
    )

    recommendations_output = llm.invoke(recommendations_prompt).content
    print(recommendations_output)

    rec_list = recommendations_output.split('\n')
    rec_ind_exp_indices = [int(x.strip()) for x in rec_list[0].split(',') if x]
    rec_res_exp_indices = [int(x.strip()) for x in rec_list[1].split(',') if x]
    rec_proj_indices = [int(x.strip()) for x in rec_list[2].split(',') if x]


        
    # Generate bullet points for each recommended item
    for index in rec_ind_exp_indices:
        description = data['industry_experience'][index]['job']
        
        bullet_points_prompt = (
            "Generate a list of 3 to 4 bullet points (most 100 characters each) that technically, clearly, and VERY VERY concisely describe the following experience "
            "in relation to the job description provided. \n"
            "Experience Description: " + description + "\n"
            "Job Description: " + job_desc + "\n"
            "Bullet Points: \n\n\n" +
            "Format your output by putting each bullet point in this: \\resumeItem{ ... }" +
            "Example output: \\resumeItem{Communicate with managers to set up campus computers used on campus} \\resumeItem{Assess and troubleshoot computer problems brought by students, faculty and staff} \\resumeItem{Maintain upkeep of computers, classroom equipment, and 200 printers across campus}"
        )

        bullet_points_output = llm.invoke(bullet_points_prompt).content
        data['industry_experience'][index]['GeneratedLLMBullets'] = bullet_points_output

    for index in rec_res_exp_indices:
        description = data['research_experience'][index]['job']
        bullet_points_prompt = (
            "Generate a list of 3 to 4 bullet points (most 100 characters each) that technically, clearly, and VERY VERY concisely describe the following experience "
            "in relation to the job description provided. \n"
            "Experience Description: " + description + "\n"
            "Job Description: " + job_desc + "\n"
            "Bullet Points: \n\n\n" +
            "Format your output by putting each bullet point in this: \\resumeItem{ ... }" +
            "Example output: \\resumeItem{Developed a full-stack web application using with Flask serving a REST API with React as the frontend} \\resumeItem{Implemented GitHub OAuth to get data from user’s repositories} \\resumeItem{Visualized GitHub data to show collaboration} \\resumeItem{Used Celery and Redis for asynchronous tasks}"
        )

        bullet_points_output = llm.invoke(bullet_points_prompt).content
        data['research_experience'][index]['GeneratedLLMBullets'] = bullet_points_output

    for index in rec_proj_indices:
        description = data['projects'][index]['description']
        techUsedDecription = ", ".join(data['projects'][index]['tech'])

        bullet_points_prompt = (
            "Generate a list of 3 to 4 bullet points (most 100 characters each) that technically, clearly, and VERY VERY concisely describe the following experience "
            "in relation to the job description provided. \n" +
            "Experience Description: " + description + "\n" +
            "Key Tech Used: " + techUsedDecription +
            "Job Description: " + job_desc + "\n" +
            "Bullet Points: \n\n\n" +
            "Format your output by putting each bullet point in this: \\resumeItem{ ... }" +
            "Example output: \\resumeItem{Developed a full-stack web application using with Flask serving a REST API with React as the frontend} \\resumeItem{Implemented GitHub OAuth to get data from user’s repositories} \\resumeItem{Visualized GitHub data to show collaboration} \\resumeItem{Used Celery and Redis for asynchronous tasks}"
        )

        bullet_points_output = llm.invoke(bullet_points_prompt).content
        data['projects'][index]['GeneratedLLMBullets'] = bullet_points_output




    # Create new lists based on the selected indices
    
    ind_exp = [data['industry_experience'][i] for i in rec_ind_exp_indices]
    res_exp = [data['research_experience'][i] for i in rec_res_exp_indices]
    projects = [data['projects'][i] for i in rec_proj_indices]

    # Update the JSON data
    data['industry_experience'] = ind_exp
    data['research_experience'] = res_exp
    data['projects'] = projects

    return data