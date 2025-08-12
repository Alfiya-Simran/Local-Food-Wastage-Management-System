import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
conn = sqlite3.connect('dataset/food_wastage.db')
c = conn.cursor()

st.title("Food Listings CRUD Operations")

# CREATE new food listing
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
        st.success("Food listing added!")

# READ current food listings
st.header("Current Food Listings")
df = pd.read_sql_query("SELECT * FROM food_listings", conn)
st.dataframe(df)

# UPDATE food quantity example
st.header("Update Food Quantity")
food_id_to_update = st.number_input("Food ID to update", min_value=1)
new_quantity = st.number_input("New Quantity", min_value=0)
if st.button("Update Quantity"):
    c.execute("UPDATE food_listings SET Quantity=? WHERE Food_ID=?", (new_quantity, food_id_to_update))
    conn.commit()
    st.success(f"Food ID {food_id_to_update} quantity updated to {new_quantity}")

# DELETE food listing example
st.header("Delete Food Listing")
food_id_to_delete = st.number_input("Food ID to delete", min_value=1, key='delete_id')
if st.button("Delete Food Listing"):
    c.execute("DELETE FROM food_listings WHERE Food_ID=?", (food_id_to_delete,))
    conn.commit()
    st.success(f"Food ID {food_id_to_delete} deleted")

st.header("Top Providers by Quantity Donated")

query = '''
SELECT p.Name, SUM(f.Quantity) AS Total_Quantity
FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Quantity DESC
LIMIT 10;
'''

df = pd.read_sql_query(query, sqlite3.connect('food_wastage.db'))

fig, ax = plt.subplots()
ax.barh(df['Name'], df['Total_Quantity'])
ax.invert_yaxis()
ax.set_xlabel('Quantity Donated')
ax.set_title('Top 10 Food Providers by Quantity')
st.pyplot(fig)


conn.close()
