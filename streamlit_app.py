import streamlit as st
import yaml
from pathlib import Path
from main import create_and_run_bot, ConfigValidator, FileManager, ConfigError

def load_config():
    with open('data_folder/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def load_resume():
    with open('data_folder/plain_text_resume.yaml', 'r') as file:
        return yaml.safe_load(file)

def main():
    st.title("Auto Jobs Applier AIHawk")
    st.write("Welcome to Auto Jobs Applier AIHawk!")

    config = load_config()
    resume = load_resume()

    # Job Preferences
    st.header("Job Preferences")
    remote = st.checkbox("Include remote jobs", value=config['remote'], key="remote_jobs_checkbox")

    
    st.subheader("Experience Level")
    experience_level = {level: st.checkbox(level.capitalize(), 
                                        value=config['experienceLevel'][level],
                                        key=f"exp_level_checkbox_{level}") 
                        for level in config['experienceLevel']}

    st.subheader("Job Types")
    job_types = {job_type: st.checkbox(job_type.capitalize(), 
                                    value=config['jobTypes'][job_type],
                                    key=f"job_type_checkbox_{job_type}") 
                for job_type in config['jobTypes']}

    st.subheader("Date Posted")
    date_filter = st.radio("Select date range", list(config['date'].keys()), 
                           index=list(config['date'].values()).index(True))

    positions = st.text_input("Desired Positions (comma-separated)", 
                            value=", ".join(config['positions']),
                            key="positions_input")

    locations = st.text_input("Desired Locations (comma-separated)", 
                            value=", ".join(config['locations']),
                            key="locations_input")

    apply_once = st.checkbox("Apply only once per company", 
                            value=config['apply_once_at_company'],
                            key="apply_once_checkbox")

    distance = st.select_slider("Distance (miles)", 
                                options=[0, 5, 10, 25, 50, 100], 
                                value=config['distance'],
                                key="distance_slider")

    company_blacklist = st.text_input("Company Blacklist (comma-separated)", 
                                    value=", ".join(config.get('company_blacklist', [])),
                                    key="company_blacklist_input")

    title_blacklist = st.text_input("Title Blacklist (comma-separated)", 
                                    value=", ".join(config.get('title_blacklist', [])),
                                    key="title_blacklist_input")
    # Personal Information
    st.header("Personal Information")
    name = st.text_input("Name", value=resume['personal_information']['name'])
    surname = st.text_input("Surname", value=resume['personal_information']['surname'])
    email = st.text_input("Email", value=resume['personal_information'].get('email', ''))
    phone = st.text_input("Phone", value=resume['personal_information'].get('phone', ''))
    zip_code = st.text_input("Zip Code", value=resume['personal_information']['zip_code'], max_chars=10)
    github = st.text_input("GitHub Profile URL (optional)", value=resume['personal_information'].get('github', ''))
    linkedin = st.text_input("LinkedIn Profile URL (optional)", value=resume['personal_information'].get('linkedin', ''))

    st.header("Education")
    education_year = st.number_input("Year of Completion", 
                                 min_value=1900, 
                                 max_value=2100, 
                                 value=int(resume['education_details'][0].get('year_of_completion', 2023)) 
                                 if resume['education_details'][0].get('year_of_completion', '').isdigit() 
                                 else 2023)

    st.header("Projects")
    project1_link = st.text_input("Project 1 Link", value=resume['projects'][0]['link'])
    project2_link = st.text_input("Project 2 Link", value=resume['projects'][1]['link'])

    # API Key
    llm_api_key = st.text_input("API Key", type="password")

    # File uploader for resume (optional)
    resume_file = st.file_uploader("Upload your resume PDF file (optional)", type=["pdf"], key="resume_uploader")
    
    # Checkbox for collect mode
    collect = st.checkbox("Only collect data job information into data.json file")

    # Run button to initiate the bot
    if st.button("Run Job Applier", key="run_job_applier_button"):
        try:
            # Construct parameters dictionary from input fields
            parameters = {
                'remote': remote,
                'experienceLevel': experience_level,
                'jobTypes': job_types,
                'date': {date_filter: True},
                'positions': [pos.strip() for pos in positions.split(',')],
                'locations': [loc.strip() for loc in locations.split(',')],
                'apply_once_at_company': apply_once,
                'distance': distance,
                'company_blacklist': [company.strip() for company in company_blacklist.split(',')],
                'title_blacklist': [title.strip() for title in title_blacklist.split(',')],
                'collectMode': collect,
                'llm_model_type': config['llm_model_type'],
                'llm_model': config['llm_model'],
                # Add other necessary parameters
            }

            # Update resume data
            resume['personal_information'].update({
                'name': name,
                'surname': surname,
                'email': email,
                'phone': phone,
                'zip_code': zip_code,
                'github': github,
                'linkedin': linkedin,
            })

            resume['education_details'][0]['year_of_completion'] = str(education_year)

            resume['projects'][0]['link'] = project1_link
            resume['projects'][1]['link'] = project2_link

            # Save updated resume data
            with open('data_folder/plain_text_resume.yaml', 'w') as file:
                yaml.dump(resume, file)

            # Handle resume file
            if resume_file:
                resume_path = Path("data_folder/output/uploaded_resume.pdf")
                resume_path.parent.mkdir(parents=True, exist_ok=True)
                resume_path.write_bytes(resume_file.getvalue())
                parameters['uploads'] = {'resume': resume_path}
            else:
                # Change 2: Added handling for when no resume is uploaded
                parameters['uploads'] = {'plainTextResume': Path('data_folder/plain_text_resume.yaml')}


            # Create and run the bot
            create_and_run_bot(parameters, llm_api_key)
            st.success("Job application process completed successfully!")
        except ConfigError as ce:
            st.error(f"Configuration error: {str(ce)}")
            st.error(f"Refer to the configuration guide for troubleshooting: https://github.com/feder-cr/Auto_Jobs_Applier_AIHawk?tab=readme-ov-file#configuration")
        except FileNotFoundError as fnf:
            st.error(f"File not found: {str(fnf)}")
            st.error("Ensure all required files are present in the data folder.")
        except RuntimeError as re:
            st.error(f"Runtime error: {str(re)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()