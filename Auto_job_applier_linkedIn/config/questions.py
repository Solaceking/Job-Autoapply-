'''
LinkedIn Auto Job Applier - Questions Configuration

This file defines resume paths and question-answer mappings for job applications.

Author:     Sai Vignesh Golla (Modified)
License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
'''

###################################################### RESUME PATHS ######################################################

# Path to your default resume file
# This is where the application will look for your resume to upload
default_resume_path = "all resumes/"

# You can also specify a specific resume file if needed
# Example: default_resume_path = "all resumes/My_Resume.pdf"


###################################################### QUESTION ANSWERS ######################################################

# Map common application questions to your answers
# The QuestionHandler will use fuzzy matching to find the best match for each question

question_answers = {
    # Work Authorization
    "Are you authorized to work in": "Yes",
    "Do you require sponsorship": "No",
    "Will you require visa sponsorship": "No",
    "Are you legally authorized": "Yes",
    
    # Experience
    "Years of experience": "3",
    "How many years of experience": "3",
    "Total years of work experience": "3",
    
    # Education
    "Do you have a degree": "Yes",
    "Highest level of education": "Bachelor's Degree",
    "What is your education level": "Bachelor's Degree",
    
    # Availability
    "When can you start": "2 weeks",
    "What is your availability": "Immediately",
    "Notice period": "2 weeks",
    "How soon can you start": "2 weeks",
    
    # Salary
    "Expected salary": "Negotiable",
    "Salary expectations": "Negotiable",
    "Desired salary": "Negotiable",
    
    # Location
    "Are you willing to relocate": "Yes",
    "Can you relocate": "Yes",
    "Willing to work remotely": "Yes",
    "Comfortable working remotely": "Yes",
    
    # General
    "Why do you want to work here": "I am excited about the opportunity to contribute to your team and grow professionally.",
    "Why are you interested": "I am passionate about this field and believe my skills align well with the role.",
    "Tell us about yourself": "I am a dedicated professional with experience in my field, eager to contribute to your organization.",
    
    # LinkedIn Profile
    "LinkedIn profile URL": "https://www.linkedin.com/in/yourprofile",
    "LinkedIn URL": "https://www.linkedin.com/in/yourprofile",
    
    # Portfolio/Website
    "Portfolio URL": "",
    "Website": "",
    "GitHub profile": "https://github.com/yourusername",
    
    # References
    "Do you have references": "Yes",
    "Can you provide references": "Yes, available upon request",
    
    # Criminal Background
    "Have you been convicted": "No",
    "Criminal record": "No",
    
    # Other Common Questions
    "Are you 18 years or older": "Yes",
    "Are you a veteran": "No",
    "Do you have a disability": "No",
    "Gender": "Prefer not to say",
    "Race/Ethnicity": "Prefer not to say",
}


###################################################### CUSTOM ANSWERS ######################################################

# You can add more specific question-answer pairs here
# The more specific your answers, the better the matching will be

# Example for specific companies or roles:
company_specific_answers = {
    # Add company-specific answers if needed
    # "Why do you want to work at Google": "Google's innovative culture...",
}

# Merge company-specific answers into main dictionary
question_answers.update(company_specific_answers)


###################################################### HELPER FUNCTIONS ######################################################

def get_answer(question: str, default: str = "") -> str:
    """
    Get answer for a given question using fuzzy matching.
    
    Args:
        question: The question text
        default: Default value to return if no match found
        
    Returns:
        The best matching answer or default value
    """
    question_lower = question.lower()
    
    # Direct match
    for key, value in question_answers.items():
        if key.lower() in question_lower:
            return value
    
    # No match found
    return default


# Export all variables
__all__ = [
    'default_resume_path',
    'question_answers',
    'get_answer',
]
