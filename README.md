# DukeAI Hackathon 2024

<img src="https://github.com/user-attachments/assets/4d4ae1b1-897d-402b-8dec-71b7fb43d062" alt="python_banner" width="85"/> <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" /> <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" /> <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" /> <img src="https://github.com/user-attachments/assets/275523c3-c0c0-4b4c-8aa7-922784ccb3d0" alt="firebase_banner" width="78"/> <img src="https://github.com/user-attachments/assets/9c2554ae-8aba-4c16-9f13-182131dfdb3c" alt="streamlit_banner" width="55"/> 

<img width="1057" alt="clinical_consent_pfp" src="https://github.com/user-attachments/assets/5e2b99cf-6e08-4e04-8772-49da66d7356a">

## 💡 About The Project 

For a novel drug to gain approval and become available to patients, it has to undergo three phases of clinical trials. Each phase requires dozens to thousands of participants to determine the appropriate dosage, effectiveness, and safety of the drug. However, there is a significant need to improve communication between potential participants and researchers. The protocols and study plans accessible to potential participants are often filled with technical jargon, making it difficult for patients to understand what to expect from the trial. This confusion can lead to participants unknowingly accepting risks or being discouraged from participating due to misunderstandings. Currently, communication between researchers and patients is largely one-sided, depending on patients to seek out information, which often results in insufficient recruitment—approximately 80% of clinical trials close due to insufficient enrollment.

To address this issue, we propose [`ClinicalConsent`](https://dukeai.streamlit.app/). By utilizing the GPT API, ClinicalConsent simplifies complex study plans and protocols into clear, understandable information for participants. Additionally, our platform includes a recommendation system that matches potential participants with suitable clinical trials based on their profiles and the available studies. ClinicalConsent will facilitate effective communication between potential participants and researchers, promoting a safer and more engaged interaction throughout the clinical trial process.


## 🚀 How to Run  
To run the application, follow the steps below:

1. **Create and Activate a Conda Environment**
   - Open your terminal and execute the following commands:
     ```bash
     conda create --name clinicalconsent python=3.10
     conda activate clinicalconsent
     ```

2. **Install Python Package Requirements**
   - Install the necessary packages by running:
     ```bash
     pip install -r requirements.txt
     ```

3. **Add OpenAI API Key**
   - Create a `.env` file and add your OpenAI API key:
     ```plaintext
     OPENAI_API_KEY=<your_openai_api_key>
     ```

4. **Run the Application**
   - Start the application using Streamlit:
     ```bash
     streamlit run app.py
     ```

&nbsp;  

## 💬 Contact
Riley Harper - rileyharper2142@gmail.com <br>
Michael Puglise - michael.puglise@duke.edu <br>
Claire Kim - hj00claire@gmail.com <br>
Yeonseo Kim - yeonseokim1223@gmail.com

## 🔗 Acknowledgments
- Duke AI Hackathon 2024
- Firebase
- Streamlit
- VSCode
- Git/GitHub 
