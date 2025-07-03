# Resume Insights: ATS Keyword Analyzer
Resume Insights: ATS Keyword Analyzer is a tool that helps job seekers optimize their resumes for applicant tracking systems

## About The Project

Resume Insights is a web application designed to give job seekers an edge in the modern hiring landscape. Many companies rely on Applicant Tracking Systems (ATS) to manage high volumes of applications. This tool simulates a core function of an ATS by comparing the text of a resume to a job description. It identifies key skills and qualifications, highlights what's missing, and provides a match score, empowering users to tailor their resumes for each application and significantly improve their chances of landing an interview.

### Built With

This project is powered by a modern technology stack:

*   **Backend:**
    ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
    ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
    ![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)
*   **Frontend:**
    ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
    ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
    ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
*   **Deployment:**
    ![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
    ![Hostinger](https://img.shields.io/badge/Hostinger-673DE6?style=for-the-badge&logo=hostinger&logoColor=white)

---

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Ensure you have Python 3.7+ installed on your system.

### Installation

1. **Setup Parent Directory:**
    ```sh
    Create a new directory for your project and navigate into it.
    ```

2.  **Clone the Backend repository:**
    ```sh
    git clone https://github.com/TechieYuvraj/Resume-Insights-Backend
    ```

3.  **Clone the Frontend repository:**
    ```sh
    git clone https://github.com/TechieYuvraj/Resume-Insights-Frontend
    ```

4.  **Set up the Backend:**
    ```sh
    pip install -r requirements.txt
    ```

5.  **Run the Backend Server:**
    ```sh
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    ```

6. **Edit `script.js`** within the `Resume-Insights-Frontend` directory and update the `API_BASE_URL` variable. 
    ```javascript
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Update this to link your backend server with frontend.
    ```

7. **Run the Frontend:**
    *   Open the `index.html` file directly in your web browser, or serve it using a local web server (e.g., `python -m http.server`):
        ```sh
        python -m http.server 3000
        ```
    *   Open your web browser and go to `http://localhost:3000/` (or the port indicated by the server).

---

## Deployment Guide

This application is designed for a decoupled deployment.

### Backend Deployment (Render)

1.  **Create a New Web Service** on Render and connect your GitHub repository.
2.  **Use the following settings** during creation:
    *   **Root Directory:** `resume-insights-backend`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000 --workers 1`
3.  Deploy the service and copy the provided `your-url.onrender.com` URL.

### Frontend Deployment (Hostinger)

1.  **Upload** the contents of the `Resume-Insights-Frontend` folder (`index.html`, `style.css`, `script.js`, `README.md`, `.gitattributes`) to your Hostinger File Manager, typically in the `public_html` directory.
2.  **Edit `script.js`** and update the `API_BASE_URL` variable with your Render backend URL.
    ```javascript
    // Before
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // After
    const API_BASE_URL = 'https://your-backend-url.onrender.com';
    ```
3.  **Save the changes.** Your site is now live.

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
