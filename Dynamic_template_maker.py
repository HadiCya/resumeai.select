import json
from string import Template

def proompting2 (data):
    # EDUCATION
    education_entries = data['education']
    education_template_txt = ""
    for i, edu in enumerate(education_entries):

        template_unit = Template(
           """

            \\resumeSubheading
            {$Name}{$Location}
            {$Level in $Majors}{$StartDate -- $EndDate}

            """
        )

        template_unit_filled = template_unit.substitute(
           {
              'Name' : edu['name'],
              'Location' : edu['location'],
              'Level' : edu['level'],
              'Majors' : ', '.join(edu['major']),
              'StartDate' : edu['start'],
              'EndDate' : edu['end']
           }
        )

        education_template_txt += template_unit_filled


    # RESEARCH EXPERIENCE
    research_entries = data['research_experience']
    research_template_txt = ""
    for i, res in enumerate(research_entries):

        template_unit = Template(
           """
            \\resumeSubheading
            {$ProjectTitle}{$StartDate -- $EndDate}
            {$University}{$Location}
            \\resumeItemListStart
                $GeneratedLLMBullets
            \\resumeItemListEnd
            """
        )

        template_unit_filled = template_unit.substitute(
           {
              'ProjectTitle' : res['project'],
              'StartDate' : res['start'],
              'EndDate' : res['end'],
              'University' : res['university'],
              'Location' : res['location'],
              'GeneratedLLMBullets' : res['GeneratedLLMBullets']
           }
        )

        research_template_txt += template_unit_filled
        

    # INDUSTRY EXPERIENCE
    industry_entries = data['industry_experience']
    industry_template_txt = ""
    for i, ind in enumerate(industry_entries):

        template_unit = Template(
           """
            \\resumeSubheading
            {$PositionTitle}{$StartDate -- $EndDate}
            {$Company}{$Location}
            \\resumeItemListStart
                $GeneratedLLMBullets
            \\resumeItemListEnd
            """
        )

        template_unit_filled = template_unit.substitute(
           {
              'PositionTitle' : ind['position'],
              'StartDate' : ind['start'],
              'EndDate' : ind['end'],
              'Company' : ind['company'],
              'Location' : ind['location'],
              'GeneratedLLMBullets' : ind['GeneratedLLMBullets']
           }
        )

        industry_template_txt += template_unit_filled
        



    # PROJECTS
    project_entries = data['projects']
    project_template_txt = ""

    for i, proj in enumerate(project_entries):
            
            template_unit = Template(
                """
                \\resumeProjectHeading
                    {\\textbf{$Name} $$|$$ \\emph{$TechUsed}}{}
                    \\resumeItemListStart
                        {$GeneratedLLMBullets}
                    \\resumeItemListEnd
            """
            )
            
            template_unit_filled = template_unit.substitute(
                {
                    'Name' : proj['project'],
                    'TechUsed' : proj['tech'],
                    'GeneratedLLMBullets' : proj['GeneratedLLMBullets']
                }
            )

            project_template_txt += template_unit_filled


    # PROGRAMMING SKILLS
    # Languages
    language_template_txt = ", ".join(data['technical_skills']['languages'])

    # Frameworks
    frameworks_template_txt = ", ".join(data['technical_skills']['frameworks'])

    # DeveloperTools
    developer_tools_template_txt = ", ".join(data['technical_skills']['dev_tools'])

    # Libraries
    library_template_txt = ", ".join(data['technical_skills']['libraries'])

    dynamic_resume_template = Template(open('dynamic_template.tex', 'r').read())

    dynamic_resume_template_txt = dynamic_resume_template.substitute(
         {
            'Name': data['personal_info']['name'],
            'PhoneNumber': data['personal_info']['phone_number'],
            'Email': data['personal_info']['email'],
            'LinkedIn': data['links']['linkedin'],
            'GitHub': data['links']['github'],
            'education_template_txt'  : education_template_txt,
            'research_template_txt' : research_template_txt,
            'industry_template_txt' : industry_template_txt,
            'project_template_txt' : project_template_txt,
            'language_template_txt' : language_template_txt,
            'frameworks_template_txt' : frameworks_template_txt,
            'developer_tools_template_txt' : developer_tools_template_txt,
            'library_template_txt' : library_template_txt
         }
    )

    f = open("test_out.tex", "w")
    f.write(dynamic_resume_template_txt)
    f.close()