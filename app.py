import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# DB Connection
conn = sqlite3.connect('dataset/food_wastage.db')
c = conn.cursor()

st.set_page_config(page_title="Local Food Wastage Management System", layout="wide")
st.title("🍽️ Local Food Wastage Management System")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📋 Manage Listings", "🔍 Filter & Contact", "📊 Analysis"])

# ===================== TAB 1 - CRUD =====================
with tab1:
    st.header("Add New Food Listing")
    with st.form("add_food"):
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1)
        expiry_date = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1)
        provider_type = st.text_input("Provider Type")
        location = st.text_input("Location")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        submitted = st.form_submit_button("Add Food")

        if submitted:
            c.execute('''INSERT INTO food_listings
                (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (food_name, quantity, expiry_date.strftime('%Y-%m-%d'), provider_id, provider_type, location, food_type, meal_type))
            conn.commit()
            st.success("✅ Food listing added!")

    st.subheader("Current Food Listings")
    df = pd.read_sql_query("SELECT * FROM food_listings", conn)
    st.dataframe(df)

    st.subheader("Update Food Quantity")
    food_id_to_update = st.number_input("Food ID to update", min_value=1)
    new_quantity = st.number_input("New Quantity", min_value=0)
    if st.button("Update Quantity"):
        c.execute("UPDATE food_listings SET Quantity=? WHERE Food_ID=?", (new_quantity, food_id_to_update))
        conn.commit()
        st.success(f"✅ Food ID {food_id_to_update} quantity updated")

    st.subheader("Delete Food Listing")
    food_id_to_delete = st.number_input("Food ID to delete", min_value=1, key='delete_id')
    if st.button("Delete Food Listing"):
        c.execute("DELETE FROM food_listings WHERE Food_ID=?", (food_id_to_delete,))
        conn.commit()
        st.success(f"🗑️ Food ID {food_id_to_delete} deleted")

# ===================== TAB 2 - Filter & Contact =====================
# ===================== TAB 2 - Filter & Contact =====================
with tab2:
    st.header("Filter Food Donations")
    cities = pd.read_sql_query("SELECT DISTINCT Location FROM food_listings", conn)['Location'].dropna().tolist()
    providers_type = pd.read_sql_query("SELECT DISTINCT Provider_Type FROM food_listings", conn)['Provider_Type'].dropna().tolist()
    food_types = pd.read_sql_query("SELECT DISTINCT Food_Type FROM food_listings", conn)['Food_Type'].dropna().tolist()

    city_filter = st.selectbox("Select City", ["All"] + cities)
    provider_filter = st.selectbox("Select Provider Type", ["All"] + providers_type)
    food_type_filter = st.selectbox("Select Food Type", ["All"] + food_types)

    query = "SELECT * FROM food_listings WHERE 1=1"
    if city_filter != "All":
        query += f" AND Location='{city_filter}'"
    if provider_filter != "All":
        query += f" AND Provider_Type='{provider_filter}'"
    if food_type_filter != "All":
        query += f" AND Food_Type='{food_type_filter}'"

    filtered_df = pd.read_sql_query(query, conn)
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        provider_ids_list = list(filtered_df['Provider_ID'].dropna().unique())

        if provider_ids_list:
            placeholders = ",".join("?" * len(provider_ids_list))
            contact_query = f"""
                SELECT Provider_ID, Name, Contact
                FROM providers
                WHERE Provider_ID IN ({placeholders})
            """
            contact_df = pd.read_sql_query(contact_query, conn, params=provider_ids_list)

            if not contact_df.empty:
                st.subheader("Provider Contact Details")
                st.dataframe(contact_df)
            else:
                st.info("No contact details found for matching providers.")
        else:
            st.info("No matching providers found.")
    else:
        st.info("No matching providers found.")


# ===================== TAB 3 - Analysis (15 Queries) =====================
with tab3:
    st.header("📊 Data Insights & Analysis")

    queries = {
        "Providers and Receivers count per city": '''
            SELECT p.City,
                   COUNT(DISTINCT p.Provider_ID) AS Provider_Count,
                   (SELECT COUNT(DISTINCT r.Receiver_ID) FROM receivers r WHERE r.City = p.City) AS Receiver_Count
            FROM providers p
            GROUP BY p.City
            ORDER BY Provider_Count DESC;
        ''',
        "Top food provider type by quantity": '''
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
            FROM food_listings
            GROUP BY Provider_Type
            ORDER BY Total_Quantity DESC
            LIMIT 5;
        ''',
        "Contact info of food providers in New York": '''
            SELECT Name, Contact FROM providers WHERE City = 'New York';
        ''',
        "Receivers who claimed the most food": '''
            SELECT r.Name, COUNT(c.Claim_ID) AS Claim_Count
            FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID
            ORDER BY Claim_Count DESC
            LIMIT 5;
        ''',
        "Total quantity of food available": '''
            SELECT SUM(Quantity) AS Total_Food_Available FROM food_listings;
        ''',
        "City with highest number of food listings": '''
            SELECT Location, COUNT(*) AS Listings_Count
            FROM food_listings
            GROUP BY Location
            ORDER BY Listings_Count DESC
            LIMIT 5;
        ''',
        "Most commonly available food types": '''
            SELECT Food_Type, COUNT(*) AS Count
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Count DESC;
        ''',
        "Number of claims made for each food item": '''
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims_Made
            FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_ID
            ORDER BY Claims_Made DESC;
        ''',
        "Provider with highest number of successful food claims": '''
            SELECT p.Name, COUNT(c.Claim_ID) AS Completed_Claims
            FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID
            ORDER BY Completed_Claims DESC
            LIMIT 5;
        ''',
        "Percentage of claims by status": '''
            SELECT Status,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS Percentage
            FROM claims
            GROUP BY Status;
        ''',
        "Average quantity of food claimed per receiver": '''
            SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY r.Receiver_ID
            ORDER BY Avg_Quantity_Claimed DESC
            LIMIT 5;
        ''',
        "Most claimed meal type": '''
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claims_Count
            FROM food_listings f JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Claims_Count DESC;
        ''',
        "Total quantity of food donated by each provider": '''
            SELECT p.Name, SUM(f.Quantity) AS Total_Quantity_Donated
            FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID
            ORDER BY Total_Quantity_Donated DESC
            LIMIT 5;
        ''',
        "Food items close to expiry (within 3 days)": '''
            SELECT Food_Name, Expiry_Date, Quantity, Location
            FROM food_listings
            WHERE DATE(Expiry_Date) <= DATE('now', '+3 days')
            ORDER BY Expiry_Date ASC;
        ''',
        "Number of claims per city": '''
            SELECT l.Location, COUNT(c.Claim_ID) AS Claims_Count
            FROM food_listings l JOIN claims c ON l.Food_ID = c.Food_ID
            GROUP BY l.Location
            ORDER BY Claims_Count DESC
            LIMIT 5;
        '''
    }

    for title, q in queries.items():
        st.subheader(title)
        df_query = pd.read_sql_query(q, conn)
        st.dataframe(df_query)

        if title in ["Top food provider type by quantity", "City with highest number of food listings", 
                     "Most commonly available food types", "Number of claims per city", "Percentage of claims by status"]:
            fig, ax = plt.subplots()
            ax.bar(df_query.iloc[:, 0], df_query.iloc[:, 1])
            ax.set_title(title)
            plt.xticks(rotation=45)
            st.pyplot(fig)

conn.close()
