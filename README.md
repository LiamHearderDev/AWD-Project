# SpeedLogger
SpeedLogger is a fun game-like web application that allows users to log their typing speed and view the logged data in an easy to read format. You can also compete with your friends for the top spot on a global leaderboard!

The goal of the CITS3403 - Agile Web Development 2025 Project is to create a web application that allows users to upload, analyze, and share data. We have done this by creating an application where data is uploaded as you use it, by playing a game that tracks data about your typing speed. You can analyse this data by viewing it in the "Statistics" page, where it is visualised and analyzed in various ways. You can then share this data by adding other users as friends, which allows them and only them to view your data. 


# The Team
|UWA Student ID|Name|GitHub Username|
|-------|----|--------------|
|23760137|Ryan Marrington|Ryan1090|   
|24059081|Ziying Zhou|ZHOUzing-M|
|23074422|Liam Hearder|LiamHearderDev|
|23163975|Quan Yan|Quan1yan|

# Overview
This project is a typing-speed testing application that allows users to practice and improve their typing skills. The application provides a user-friendly interface where users can take typing tests, view their results, and track their progress over time. 

Along the header, you can find a series of tabs that allow you to navigate through the application. The tabs include:
- **Home**: The main page of the application, where users can read about the application and its features.
- **Game**: The main feature of the application, where users can take typing tests and see their results.
- **Stats**: A page that displays the user's typing speed, accuracy, and more over a given period of time, allowing them to track their progress.
- **Leaderboard**: A page that displays the top scores of users, allowing them to compete with friends and others.
- **Profile**: A page that allows users to view and edit their profile information, including their username and password.

# Technologies Used
Frontend:
- HTML and CSS for the user interface
- JavaScript for interactivity and functionality
- Chart.js for creating charts and visualizing data
- Bootstrap for responsive design
- jQuery for DOM manipulation and event handling

Backend:
- Flask for creating the web server, handling requests, and building the frontend
- Python for server-side logic and data processing
- SQLite for storing user data, game results, etc.


# How to run

## Prerequisites
- python3
- pip

## Installation
### 1. Clone the repository:
```bash
git clone https://github.com/LiamHearderDev/AWD-Project.git
cd AWD-Project
```

### 2. Create a virtual environment, to install the required packages:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the required packages:
```bash
python -m pip install -r requirements.txt
```

### 4. Create the database:
```bash
python -m flask db init
python -m flask db migrate
python -m flask db upgrade
```

### 5. Create environment variables:
```bash
echo > .flaskenv "FLASK_APP=run.py" && echo >> .flaskenv "FLASK_ENV=development" && echo >> .flaskenv "SECRET_KEY=<insert_your_super_secret_key>" 
```
or, alternatively:
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
export SECRET_KEY=<insert_your_super_secret_key>
```

### 6. Run the application:
```bash
python -m flask run
```
Or alternatively, if in a docker container:
```bash
python -m flask run --host=0.0.0.0              # to allow access from outside the container
```

### 7. Open SpeedLogger
Head to ``` http://localhost:5000 ``` and have fun!
