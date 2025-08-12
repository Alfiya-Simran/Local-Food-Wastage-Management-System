# 🍽️ Local Food Wastage Management System

A Streamlit web application that helps manage surplus food and minimize wastage by connecting donors with NGOs or individuals in need. The system provides an easy-to-use interface for logging surplus food details, tracking donations, and promoting sustainable food distribution.

## 🚀 Live Demo
[Streamlit App](https://local-food-wastage-management-system-huuozmjddhtthn7w9x5kdr.streamlit.app/)

---

## 📌 Features
- **Food Donation Form** – Donors can log surplus food details.
- **Recipient Matching** – Match food with NGOs or people nearby.
- **Tracking Dashboard** – View donation history and status.
- **Sustainability Goals** – Promote zero food wastage and community help.
- **Responsive UI** – Works on desktop and mobile.

---

## 🛠️ Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend:** Python
- **Database:** CSV / SQLite (depending on implementation)
- **Libraries:** Pandas, NumPy, etc.

---

## 📂 Project Structure
```bash
├── app.py                          # Main Streamlit application
├── Local Food Wastage Management System.ipynb  # Jupyter notebook for data analysis/modeling
├── requirements.txt                # Python dependencies
├── data/
│   ├── providers_data.csv           # Information about food providers
│   ├── receivers_data.csv           # Information about receivers
│   ├── food_listings_data.csv       # Listings of surplus food
│   ├── claims_data.csv              # Data on claimed food
│   └── food_wastage.db              # SQLite database
└── README.md                       # Project documentation
```

---

## 🚀 Features
- Provider Management: Add and manage food providers’ details.

- Receiver Management: Register and track food receivers.

- Food Listings: Post surplus food availability.

- Claims Tracking: Manage and record food claims by receivers.

- Database Integration: SQLite backend for persistent storage.

- Data Analysis: Insights on food wastage trends using Jupyter Notebook.

---

## ⚙️ Installation & Setup
1. **Clone the repository**
```bash
git clone https://github.com/Alfiya-Simran/local-food-wastage-management-system.git
cd local-food-wastage-management
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Run the app locally**
```bash
streamlit run app.py
```
4. **Open the app in your browser at http://localhost:8501**

---

## 📊 Dataset
- The data/ folder contains:

  - CSV files with provider, receiver, food listings, and claims data.

  - SQLite database (food_wastage.db) for integrated storage.

---

## 📒 Jupyter Notebook
- The Local Food Wastage Management System.ipynb notebook includes:

  - Data exploration

  - Statistical analysis

  - Visualizations for wastage trends

---

## 🤝 Contributing
Pull requests are welcome! If you'd like to improve the app, fork the repository and submit a PR.

---

## 📄 License
This project is licensed under the MIT License – see the LICENSE file for details.
