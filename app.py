import streamlit as st
import pandas as pd
import openai

# Set OpenAI API Key (Use your own key here)
openai.api_key = "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"  # Replace with your OpenAI API key

# Load the datasets (replace with your paths or upload them)
recipes_path = 'recipes.csv'
reviews_path = 'reviews.csv'

recipes = pd.read_csv(recipes_path, on_bad_lines='skip')
reviews = pd.read_csv(reviews_path, on_bad_lines='skip')

# Preprocessing and Cleaning
nutritional_columns = [
    'RecipeId', 'Name', 'Calories', 'FatContent', 'SaturatedFatContent',
    'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent'
]
recipes.columns = recipes.columns.str.strip()
recipes = recipes[nutritional_columns].dropna()

# Recommendation System
def recommend_recipes(user_prefs, recipes_df, top_n=5):
    nutrition_columns = ['Calories', 'FatContent', 'SodiumContent', 'CarbohydrateContent', 'ProteinContent']
    # ... (rest of the recommendation system code) ...

# Direct OpenAI Integration for Chatbot Query
def chatbot_query(query):
    prompt = f"""
    You are a helpful assistant that answers questions about recipes and nutrition.
    Here is a list of recipes: {', '.join(recipes['Name'].to_list())}
    Answer the following query: {query}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit Frontend UI for Chatbot Page
def user_input_form_page3():
    st.title("Chatbot: Ask Me About Recipes & Nutrition")

    user_query = st.text_input("Ask me anything about recipes or nutrition:")

    if user_query:
        response = chatbot_query(user_query)
        st.write("Answer: ", response)

# Main function with Streamlit pages
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Demographics & Activity", "Page 2: Nutrition Preferences", "Page 3: Chatbot"))

    # Page-specific logic...
    if page == "Page 3: Chatbot":
        user_input_form_page3()

if __name__ == "__main__":
    main()
