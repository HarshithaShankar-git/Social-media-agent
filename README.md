# 🌟 Social Media Agent — Groq + Streamlit

An intelligent and lightweight **AI-powered Social Media Content Generator** that creates:
- Engaging captions  
- Relevant hashtags  
- A complete 7-day content plan  

Powered by **Groq’s FREE Llama models** and built using **Streamlit**, this app provides instant, high-quality content generation.

Perfect for students, creators, marketers, and businesses who want fast, reliable content.

---

## 📘 Overview
This project is an **AI Agent** that takes user input (topic, platform, tone, number of captions) and generates:
- Multiple captions  
- Hashtags  
- A full 7-day content plan  

It uses a **Groq LLM** through API and provides a clean **Streamlit UI** for seamless interaction.

---

## 🌐 Live Demo
👉 **Deployed App:**  
https://harshithashankar-git-social-media-agent-app-wrqla6.streamlit.app/

---

## 🖼️ Screenshots

### 🏠 Home Screen  
![Home](screenshots/Home.png)

---

### ✨ Generated Output — Sample 1  
![Output 1](screenshots/Output-1.png)

---

### ✨ Generated Output — Sample 2  
![Output 2](screenshots/Output-2.png)

---

### ✨ Generated Output — Sample 3  
![Output 3](screenshots/Output-3.png)

---

## 🚀 Features
- Generate **any number** of social media captions  
- Automatic **6 hashtags**  
- AI-generated **7-day content plan**  
- Copy-to-clipboard buttons for captions & hashtags  
- Download captions as **CSV**  
- Download raw model output as **TXT**  
- Recent generations stored within session  
- Clean, user-friendly Streamlit interface  

---

## ⚠️ Limitations
- Internet connection required for Groq API  
- Output quality depends on the selected Groq model  
- Only text-based generation (no image generation yet)  
- Session history clears on page reload  
- Not integrated with actual social media posting APIs  

---

## 🧠 Tech Stack & APIs
### **Languages & Frameworks**
- Python 3.11.9  
- Streamlit  

### **Libraries**
- Groq Python SDK  
- pandas  
- python-dotenv (optional for local secrets)

### **APIs**
- **Groq LLM API** (free for this project)

---

## 🛠️ Local Setup & Run (Windows PowerShell)

### 1️⃣ Clone the repository
```powershell
git clone https://github.com/HarshithaShankar-git/social-media-agent.git
cd social-media-agent
