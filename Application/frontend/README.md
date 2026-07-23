# ClubSphere Frontend

A modern, fast, and responsive frontend web application built with [React](https://react.dev/) and [Vite](https://vitejs.dev/). 

## 🚀 Features

* **Lightning Fast HMR:** Powered by Vite for instant feedback during development.
* **Component-Based Architecture:** Built using React functional components and hooks.
* **Modern JavaScript:** Utilizing ES6+ syntax.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your local machine:
* [Node.js](https://nodejs.org/en/download) ( v24.18.0 LTS Windows Installer (.msi) or higher )
* npm (comes with Node.js)

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayush-puhan/MAY2026-Team-073.git
   cd Application
   ```

2. **Set up the Backend (Python):**
   Ensure you have Python installed, then install the required dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up the Frontend (Node.js):**
   ```bash
   cd ../frontend
   npm install
   ```

## 🏃 Running the Application (Local Development)

The frontend is configured to run alongside a `json-server` mock backend. To start the application and test it out locally:

1. **Start the mock database server:**
   ```bash
   npm run server
   ```
   *The mock API server will run on `http://localhost:5000`*

2. **Start the development server (in a new terminal):**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Open your browser and navigate to `http://localhost:5173`

## 🧪 Testing the Application

### Sample Login Credentials
You can use the following pre-configured mock credentials to test various role-based workflows and access levels within the application:

* **Student / Club Leader (All Club Roles):**
  - **Email:** `user1@campus.edu`
  - **Password:** `Password@123`
  - *(This user is a member/president of multiple clubs, perfect for testing the Committee Workspace and Club Management features.)*

* **University Admin (Student Affairs / Dean):**
  - **Email (Student Affairs Office):** `user10@campus.edu`
  - **Email (Dean of Student Welfare):** `user12@campus.edu`
  - **Password:** `Password@123`
  - *(Use these to test the University Admin approval queues, club creation requests, and overview metrics for their respective universities.)*

* **Faculty Advisor:**
  - **Email:** `user4@campus.edu`
  - **Password:** `Password@123`
  - *(Use this to test the Faculty Advisor dashboard and club approvals. They only see clubs they are assigned to supervise.)*

* **System Admin:**
  - **Email:** `user5@campus.edu`
  - **Password:** `Password@123`
  - *(Use this to test the System Admin dashboard and global settings.)*

*(Note: All seeded test users in the mock database share the password `Password@123`)*

## 🏗️ Building for Production

1. **Create an optimized, production-ready build:**
   ```bash
   npm run build
   ```

2. **Preview the production build locally:**
   ```bash
   npm run preview
   ```

## 🤝 Contributing
* Fork the repository
* Create your feature branch (`git checkout -b feature/AmazingFeature`)
* Commit your changes (`git commit -m 'Add some AmazingFeature'`)
* Push to the branch (`git push origin feature/AmazingFeature`)
* Open a Pull Request
