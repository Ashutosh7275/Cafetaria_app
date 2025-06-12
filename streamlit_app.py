import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Cafeteria Management System",
    page_icon="☕",
    layout="wide",
)

# --- Helper Functions ---
def initialize_data():
    """Initializes sample menu and order data if not already in session state."""
    if 'menu_items' not in st.session_state:
        st.session_state.menu_items = pd.DataFrame({
            'Item ID': [1, 2, 3, 4, 5, 6, 7, 8],
            'Name': ['Coffee', 'Tea', 'Sandwich', 'Salad', 'Pizza Slice', 'Burger', 'Fries', 'Juice'],
            'Category': ['Beverage', 'Beverage', 'Snack', 'Meal', 'Meal', 'Meal', 'Side', 'Beverage'],
            'Price': [50.00, 40.00, 120.00, 150.00, 100.00, 180.00, 70.00, 60.00],
            'Available': [True, True, True, True, True, False, True, True]
        })

    if 'orders' not in st.session_state:
        st.session_state.orders = pd.DataFrame(columns=['Order ID', 'Timestamp', 'Items', 'Total Amount', 'Status'])

    if 'order_id_counter' not in st.session_state:
        st.session_state.order_id_counter = 1

    if 'cart' not in st.session_state:
        st.session_state.cart = []

def get_available_menu():
    """Returns the currently available menu items."""
    return st.session_state.menu_items[st.session_state.menu_items['Available'] == True]

def calculate_total_savings(cart_df):
    """Calculate any applicable discounts and total savings"""
    total_amount = cart_df['Subtotal'].sum()
    discount = 0

    # Apply different discount rules
    if total_amount > 500:
        discount = total_amount * 0.10  # 10% off on orders above ₹500
    elif len(cart_df) >= 3:
        discount = total_amount * 0.05  # 5% off on 3 or more items

    return discount

def get_estimated_time():
    """Calculate estimated preparation time based on items in cart"""
    base_time = 10  # Base preparation time in minutes
    items_count = sum(item['Quantity'] for item in st.session_state.cart)
    return base_time + (items_count * 2)  # 2 minutes per item

def format_currency(amount):
    return f"₹{amount:,.2f}"

# --- Main Application ---
st.title("☕ Cafeteria Management System")
st.markdown("---")

# Initialize data
initialize_data()

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["View Menu & Order", "View Orders", "Manage Menu"])
st.sidebar.markdown("---")
st.sidebar.info("Navigate through the cafeteria system using the sidebar.")

# --- Page 1: View Menu & Order ---
if page == "View Menu & Order":
    st.header("🍽️ Menu")

    available_menu_df = get_available_menu()

    if available_menu_df.empty:
        st.warning("No items are currently available on the menu.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader("Place Your Order")
            selected_item_name = st.selectbox("Select Item", options=available_menu_df['Name'])
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        with col3:
            st.write("")  # for alignment
            st.write("")  # for alignment
            if st.button("Add to Cart", use_container_width=True):
                if selected_item_name:
                    item_details = available_menu_df[available_menu_df['Name'] == selected_item_name].iloc[0]
                    st.session_state.cart.append({
                        'Item ID': item_details['Item ID'],
                        'Name': selected_item_name,
                        'Price': item_details['Price'],
                        'Quantity': quantity,
                        'Subtotal': item_details['Price'] * quantity
                    })
                    st.success(f"Added {quantity} x {selected_item_name} to cart!")

        st.markdown("---")
        st.subheader("Your Cart 🛒")
        if not st.session_state.cart:
            st.info("Your cart is empty. Add items from the menu above.")
        else:
            cart_df = pd.DataFrame(st.session_state.cart)

            # Enhanced cart display with columns
            cart_cols = st.columns([3, 1, 1, 1, 1])
            with cart_cols[0]:
                st.markdown("**Item**")
            with cart_cols[1]:
                st.markdown("**Quantity**")
            with cart_cols[2]:
                st.markdown("**Price**")
            with cart_cols[3]:
                st.markdown("**Subtotal**")
            with cart_cols[4]:
                st.markdown("**Actions**")

            for idx, item in cart_df.iterrows():
                with cart_cols[0]:
                    st.write(item['Name'])
                with cart_cols[1]:
                    new_qty = st.number_input("", min_value=1, value=item['Quantity'],
                                            key=f"qty_{idx}", label_visibility="collapsed")
                    if new_qty != item['Quantity']:
                        st.session_state.cart[idx]['Quantity'] = new_qty
                        st.session_state.cart[idx]['Subtotal'] = new_qty * item['Price']
                        st.experimental_rerun()
                with cart_cols[2]:
                    st.write(format_currency(item['Price']))
                with cart_cols[3]:
                    st.write(format_currency(item['Subtotal']))
                with cart_cols[4]:
                    if st.button("🗑️", key=f"remove_{idx}"):
                        st.session_state.cart.pop(idx)
                        st.experimental_rerun()

            # Order summary with advanced features
            st.markdown("---")
            st.subheader("Order Summary")

            total_amount = cart_df['Subtotal'].sum()
            discount = calculate_total_savings(cart_df)
            final_amount = total_amount - discount
            est_time = get_estimated_time()

            summary_cols = st.columns(4)
            with summary_cols[0]:
                st.metric("Items in Cart", len(cart_df))
            with summary_cols[1]:
                st.metric("Subtotal", format_currency(total_amount))
            with summary_cols[2]:
                st.metric("Savings", format_currency(discount))
            with summary_cols[3]:
                st.metric("Final Amount", format_currency(final_amount))

            st.info(f"🕒 Estimated preparation time: {est_time} minutes")

            with st.expander("Order Preferences"):
                special_instructions = st.text_area("Special Instructions",
                    placeholder="Any special requests? (e.g., extra spicy, no onions, etc.)")
                preferred_time = st.time_input("Preferred Pickup Time",
                    value=datetime.now().time())

            if st.button("Place Order", type="primary", use_container_width=True):
                if st.session_state.cart:
                    order_id = st.session_state.order_id_counter
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    items_ordered = cart_df.to_dict('records')  # More detailed storage
                    new_order = pd.DataFrame([{
                        'Order ID': order_id,
                        'Timestamp': timestamp,
                        'Items': items_ordered,
                        'Total Amount': final_amount,
                        'Status': 'Pending',
                        'Instructions': special_instructions,
                        'Pickup Time': preferred_time.strftime("%H:%M:%S")
                    }])
                    st.session_state.orders = pd.concat([st.session_state.orders, new_order], ignore_index=True)
                    st.session_state.order_id_counter += 1
                    st.session_state.cart = []  # Clear cart after placing order
                    st.success(f"Order #{order_id} placed successfully!")
                    st.balloons()
                else:
                    st.warning("Your cart is empty. Cannot place an empty order.")

        st.markdown("---")
        st.subheader("Full Menu")
        st.dataframe(available_menu_df[['Name', 'Category', 'Price']], use_container_width=True)


# --- Page 2: View Orders ---
elif page == "View Orders":
    st.header("📋 Order History")

    if st.session_state.orders.empty:
        st.info("No orders have been placed yet.")
    else:
        orders_display_df = st.session_state.orders.copy()
        # For display purposes, convert 'Items' list of dicts to a more readable string
        orders_display_df['Items Summary'] = orders_display_df['Items'].apply(
            lambda items: ", ".join([f"{item['Name']} (x{item['Quantity']})" for item in items])
        )

        st.dataframe(orders_display_df[['Order ID', 'Timestamp', 'Items Summary', 'Total Amount', 'Status']], use_container_width=True)

        st.markdown("---")
        st.subheader("Update Order Status")
        if not st.session_state.orders.empty:
            order_ids = st.session_state.orders['Order ID'].tolist()
            selected_order_id_update = st.selectbox("Select Order ID to Update", options=order_ids, key="update_order_select")
            new_status = st.selectbox("New Status", options=['Pending', 'Preparing', 'Ready', 'Completed', 'Cancelled'], key="update_status_select")

            if st.button("Update Status", use_container_width=True):
                order_index = st.session_state.orders[st.session_state.orders['Order ID'] == selected_order_id_update].index
                if not order_index.empty:
                    st.session_state.orders.loc[order_index, 'Status'] = new_status
                    st.success(f"Status for Order #{selected_order_id_update} updated to '{new_status}'.")
                    # No need to st.rerun() usually, Streamlit handles it.
                else:
                    st.error("Order ID not found.")
        else:
            st.info("No orders to update.")


# --- Page 3: Manage Menu ---
elif page == "Manage Menu":
    st.header("⚙️ Manage Menu Items")

    menu_editor_df = st.session_state.menu_items.copy() # Work on a copy

    st.subheader("Current Menu")
    edited_df = st.data_editor(
        menu_editor_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Available": st.column_config.CheckboxColumn(
                "Available?",
                default=False,
            ),
            "Price": st.column_config.NumberColumn(
                "Price (₹)",
                min_value=0.0,
                format="₹%.2f",
            )
        }
    )

    if st.button("Save Menu Changes", type="primary", use_container_width=True):
        # Basic validation: Check for duplicate Item IDs if new rows were added
        if edited_df['Item ID'].duplicated().any():
            st.error("Item IDs must be unique. Please correct the duplicates.")
        else:
            st.session_state.menu_items = edited_df.reset_index(drop=True)
            st.success("Menu updated successfully!")

    st.markdown("---")
    st.info("""
        **How to use the Menu Editor:**
        - **Edit Cells:** Double-click on a cell to change its value.
        - **Add Row:** Scroll to the bottom of the table and click the '+' button in the last empty row. Ensure you add a unique 'Item ID'.
        - **Delete Row:** Select a row by clicking on its row number on the left, then press the 'Delete' key.
        - **Availability:** Check/uncheck the 'Available' box to make items visible/hidden on the order page.
        - **Save Changes:** Click the 'Save Menu Changes' button to apply your modifications.
    """)
