# Import Libraries
from dotenv import load_dotenv
load_dotenv()  # Load all environment variables

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import matplotlib.pyplot as plt
from PIL import Image

#display image reszie
def resize_image(image_path, max_width=600):
    image = Image.open(image_path)
    width_percent = max_width / float(image.size[0])
    new_height = int(float(image.size[1]) * width_percent)
    resized_image = image.resize((max_width, new_height))  # Remove Image.ANTIALIAS
    return resized_image

# Configure GenAI Key
genai.configure(api_key="AIzaSyAi78JTbfUWkHa96gnzOJlgEhfaWgMIhis")

def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, image[0]])
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit Page Configuration
st.set_page_config(
    page_title="The Nutritionist",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"  # This keeps the sidebar always visible
)

# Custom CSS for Navbar Styling
st.markdown("""
    <style>
        .navbar {
            background-color: #42405f;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'Arial', sans-serif;
        }
        .navbar button {
            background: none;
            border: none;
            color: white;
            font-size: 16px;
            font-weight: bold;
            margin: 0 15px;
            cursor: pointer;
        }
        .navbar button:hover {
            text-decoration: underline;
        }
        .navbar .brand {
            font-size: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            color: white;
        }
        .home-container {
            text-align: center;
            margin-top: 50px;
        }
        .home-image {
            max-width: 80%;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Ensure session state is initialized
if "selected_section" not in st.session_state:
    st.session_state.selected_section = "Home"

# Sidebar Navigation
selected_section = st.sidebar.radio(
    "Navigation", ["Home", "Analyze", "About", "Contact"],
    index=["Home", "Analyze", "About", "Contact"].index(st.session_state.selected_section)
)

# Home Section
if selected_section == "Home":
    st.markdown('<div class="home-container">', unsafe_allow_html=True)
    st.title("🍎 The Nutritionist")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
            **Welcome to The Nutritionist!**  
            A powerful AI tool to analyze food and provide nutritional insights.  
            
            - 🍏 Check calorie content  
            - 🥗 Get diet suggestions  
            - 🔬 AI-powered analysis  
        """)

        if st.button("🚀 Get Started"):
            st.session_state.selected_section = "Analyze"
            st.rerun()

    with col2:
        st.image("home.png", caption="", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Analyze Section
elif selected_section == "Analyze":
    st.header("🔍 Analyze Your Food")
    st.write("Upload an image of your meal, and we'll analyze its nutritional content.")

    diet_type = st.selectbox("Select your dietary preference:", ["No Preference", "Vegetarian", "Vegan", "Keto", "Paleo"])
    calorie_limit = st.slider("Set your daily calorie limit (kcal):", min_value=1000, max_value=4000, step=100, value=2000)

    uploaded_file = st.file_uploader("Upload a meal image (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=400)
        st.success("Image uploaded successfully!")

    submit = st.button("Analyze Nutritional Content")

    input_prompt = f"""
    Analyze the food in this image:
    1. List food items and calories.
    2. Assess meal healthiness.
    3. Suggest improvements for a {diet_type} diet.
    4. Keep it under {calorie_limit} kcal daily.
    """

    if submit and uploaded_file:
        try:
            with st.spinner("Analyzing..."):
                image_data = input_image_setup(uploaded_file)
                response = get_gemini_response(input_prompt, image_data)

                # Placeholder macronutrient values (Example Data)
                nutrients = {"Carbs": 50, "Proteins": 30, "Fats": 20, "Calories": 400}

                # Create Matplotlib Figures
                fig, ax = plt.subplots(figsize=(4, 4))  # Reduce size
                fig_bar, ax_bar = plt.subplots(figsize=(5, 3))  # Reduce size

                # Pie Chart
                ax.pie(nutrients.values(), labels=nutrients.keys(), autopct="%1.1f%%", 
                       colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
                ax.set_title("Macronutrient & Calorie Breakdown")

                # Bar Chart
                ax_bar.bar(nutrients.keys(), nutrients.values(), 
                           color=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
                ax_bar.set_title("Macronutrient & Calorie Composition")
                ax_bar.set_ylabel("Grams / kcal")

                # Display Charts
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.pyplot(fig)  # Pie Chart
                with col2:
                    st.pyplot(fig_bar)  # Bar Chart

                # Show AI Description Below
                st.subheader("Nutritional Analysis")
                st.write(response)

        except Exception as e:
            st.error(f"Error: {e}")

# About Section
elif selected_section == "About":
    st.header("ℹ️ About Us")
    
    st.write("""
    **Welcome to The Nutritionist!** 🍎  
    We are on a mission to help people make healthier food choices using AI-powered analysis.  
    Whether you're tracking calories, following a specific diet, or just curious about your meals,  
    our tool provides insights tailored to your needs.  
    
    ### 🔬 How It Works:
    1. 📸 **Upload a photo** of your meal.
    2. 🤖 **AI analyzes** the food content and estimates nutritional values.
    3. 🥗 **Get personalized recommendations** based on your dietary goals.
    
    ### 🌟 Why Choose The Nutritionist?
    - ✅ **AI-Powered**: Uses state-of-the-art machine learning for accurate analysis.
    - ✅ **Customizable**: Supports multiple dietary preferences (Vegan, Keto, Paleo, etc.).
    - ✅ **User-Friendly**: Just upload a photo—no manual input required!
    - ✅ **Health Insights**: Provides tips on how to improve your meal choices.
    
    **Join thousands of users taking control of their nutrition today!** 🚀
    """)

   # Display resized image
    resized_image = resize_image("about_us.jpg", max_width=500)  # Adjust width as needed
    st.image(resized_image, caption="Your AI-Powered Nutrition Assistant", use_container_width =False)

    st.subheader("🎯 Our Vision")
    st.write("""
    We believe in empowering individuals with knowledge about their nutrition.  
    Our goal is to make **healthy eating easy, accessible, and enjoyable** for everyone.
    """)

    st.subheader("📈 Future Plans")
    st.write("""
    - 🥦 **Expanded Food Database**: Adding more global cuisines and meal types.  
    - 📊 **Nutrient Tracking**: Log your meals and track macros over time.  
    - 🛍️ **Grocery Recommendations**: AI-driven shopping lists based on your dietary goals.  
    """)

# Contact Section
elif selected_section == "Contact":
    st.header("📞 Contact Us")
    
    st.write("""
    Have questions, suggestions, or need support?  
    We'd love to hear from you! Reach out to us via the following channels:
    """)

    st.subheader("📧 Email")
    st.write("support@thenutritionist.com")

    st.subheader("🌍 Website")
    st.write("[Visit The Nutritionist](#)")

    st.subheader("📍 Office Address")
    st.write("Lokmanya Nagar, PCE Nagpur, Nagpur, Maharashtra")


    st.subheader("📱 Follow Us on Social Media")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("📘 [Facebook](#)")
    with col2:
        st.markdown("🐦 [Twitter](#)")
    with col3:
        st.markdown("📸 [Instagram](#)")

    st.subheader("💬 Support & Feedback")
    st.write("""
    Got feedback or need assistance? Join our community forum or reach out through our  
    live chat support available from **9 AM - 6 PM (Monday to Friday).**
    """)

    st.subheader("🚀 Business Inquiries")
    st.write("""
    Interested in partnerships, API integration, or bulk usage?  
    **Email us at:** business@thenutritionist.com  
    """)
