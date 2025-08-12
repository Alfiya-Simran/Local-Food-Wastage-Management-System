import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# DB connection
conn = sqlite3.connect('dataset/food_wastage.db')
c = conn.cursor()

st.title("Local Food Wastage Management System")

# =========================
# CRUD Operations
# =========================
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
                  (food_name, quantity, expiry_date.strftime('%Y-%m-%d'),
                   provider_id, provider_type, location, food_type, meal_type))
        conn.commit()
        st.success("Food listing added!")

st.header("Current Food Listings")
df = pd.read_sql_query("SELECT * FROM food_listings", conn)
st.dataframe(df)

st.header("Update Food Quantity")
food_id_to_update = st.number_input("Food ID to update", min_value=1)
new_quantity = st.number_input("New Quantity", min_value=0)
if st.button("Update Quantity"):
    c.execute("UPDATE food_listings SET Quantity=? WHERE Food_ID=?",
              (new_quantity, food_id_to_update))
    conn.commit()
    st.success(f"Food ID {food_id_to_update} quantity updated to {new_quantity}")

st.header("Delete Food Listing")
food_id_to_delete = st.number_input("Food ID to delete", min_value=1, key='delete_id')
if st.button("Delete Food Listing"):
    c.execute("DELETE FROM food_listings WHERE Food_ID=?", (food_id_to_delete,))
    conn.commit()
    st.success(f"Food ID {food_id_to_delete} deleted")

# =========================
# Chart
# =========================
st.header("Top Providers by Quantity Donated")
query_chart = '''
SELECT p.Name, SUM(f.Quantity) AS Total_Quantity
FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Quantity DESC
LIMIT 10;
'''
df_chart = pd.read_sql_query(query_chart, conn)
fig, ax = plt.subplots()
ax.barh(df_chart['Name'], df_chart['Total_Quantity'])
ax.invert_yaxis()
ax.set_xlabel('Quantity Donated')
ax.set_title('Top 10 Food Providers by Quantity')
st.pyplot(fig)

# =========================
# SQL Analysis Queries
# =========================
st.header("SQL Analysis — 15 Insights")

queries = {
    "1. Providers and Receivers count per city": '''
        SELECT p.City,
               COUNT(DISTINCT p.Provider_ID) AS Provider_Count,
               (SELECT COUNT(DISTINCT r.Receiver_ID) FROM receivers r WHERE r.City = p.City) AS Receiver_Count
        FROM providers p
        GROUP BY p.City
        ORDER BY Provider_Count DESC;
    ''',
    "2. Top food provider type by quantity": '''
        SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
        FROM food_listings
        GROUP BY Provider_Type
        ORDER BY Total_Quantity DESC
        LIMIT 5;
    ''',
    "3. Contact info of food providers in 'New York'": '''
        SELECT Name, Contact FROM providers WHERE City = 'New York';
    ''',
    "4. Receivers who claimed the most food": '''
        SELECT r.Name, COUNT(c.Claim_ID) AS Claim_Count
        FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        GROUP BY r.Receiver_ID
        ORDER BY Claim_Count DESC
        LIMIT 5;
    ''',
    "5. Total quantity of food available": '''
        SELECT SUM(Quantity) AS Total_Food_Available FROM food_listings;
    ''',
    "6. City with highest number of food listings": '''
        SELECT Location, COUNT(*) AS Listings_Count
        FROM food_listings
        GROUP BY Location
        ORDER BY Listings_Count DESC
        LIMIT 5;
    ''',
    "7. Most commonly available food types": '''
        SELECT Food_Type, COUNT(*) AS Count
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Count DESC;
    ''',
    "8. Number of claims made for each food item": '''
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims_Made
        FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY f.Food_ID
        ORDER BY Claims_Made DESC;
    ''',
    "9. Provider with highest number of successful claims": '''
        SELECT p.Name, COUNT(c.Claim_ID) AS Completed_Claims
        FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID
        ORDER BY Completed_Claims DESC
        LIMIT 5;
    ''',
    "10. Percentage of claims by status": '''
        SELECT Status,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS Percentage
        FROM claims
        GROUP BY Status;
    ''',
    "11. Average quantity of food claimed per receiver": '''
        SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Receiver_ID
        ORDER BY Avg_Quantity_Claimed DESC
        LIMIT 5;
    ''',
    "12. Most claimed meal type": '''
        SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Claims_Count
        FROM food_listings f JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY f.Meal_Type
        ORDER BY Claims_Count DESC;
    ''',
    "13. Total quantity of food donated by each provider": '''
        SELECT p.Name, SUM(f.Quantity) AS Total_Quantity_Donated
        FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Provider_ID
        ORDER BY Total_Quantity_Donated DESC
        LIMIT 5;
    ''',
    "14. Food items close to expiry (within 3 days)": '''
        SELECT Food_Name, Expiry_Date, Quantity, Location
        FROM food_listings
        WHERE DATE(Expiry_Date) <= DATE('now', '+3 days')
        ORDER BY Expiry_Date ASC;
    ''',
    "15. Number of claims per city": '''
        SELECT l.Location, COUNT(c.Claim_ID) AS Claims_Count
        FROM food_listings l JOIN claims c ON l.Food_ID = c.Food_ID
        GROUP BY l.Location
        ORDER BY Claims_Count DESC
        LIMIT 5;
    '''
}

for title, sql in queries.items():
    with st.expander(title):
        st.code(sql, language="sql")
        try:
            df_query = pd.read_sql_query(sql, conn)
            st.dataframe(df_query)
        except Exception as e:
            st.error(f"Error executing query: {e}")

conn.close()
