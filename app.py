import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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

# Aggregate reviews to compute average ratings
average_ratings = reviews.groupby('RecipeId')['Rating'].mean().reset_index()
average_ratings.rename(columns={'Rating': 'AverageRating'}, inplace=True)
recipes = recipes.merge(average_ratings, on='RecipeId', how='left')
recipes['AverageRating'] = recipes['AverageRating'].fillna(0)

# Recommendation System (as previously defined)
def recommend_recipes(user_prefs, recipes_df, top_n=5):
    nutrition_columns = ['Calories', 'FatContent', 'SodiumContent', 'CarbohydrateContent', 'ProteinContent']
    
    # Fill missing values in recipes dataset with median
    for col in nutrition_columns:
        recipes_df[col] = recipes_df[col].fillna(recipes_df[col].median())
    
    # Ensure user preferences have all necessary columns
    for col in nutrition_columns:
        if col not in user_prefs:
            user_prefs[col] = recipes_df[col].median()  # Fill missing user preference with the median
    
    # Scale nutritional data
    scaler = MinMaxScaler()
    recipes_scaled = recipes_df.copy()
    recipes_scaled[nutrition_columns] = scaler.fit_transform(recipes_df[nutrition_columns])
    
    # Prepare user preferences for scaling
    user_vector = pd.DataFrame([user_prefs], columns=nutrition_columns)
    user_vector = scaler.transform(user_vector)
    
    # Compute cosine similarity
    similarity = cosine_similarity(user_vector, recipes_scaled[nutrition_columns])
    recipes_scaled['Similarity'] = similarity[0]
    
    # Sort by similarity and rating
    recommendations = recipes_scaled.sort_values(by=['Similarity', 'AverageRating'], ascending=[False, False])
    return recommendations.head(top_n)

# LangChain Chatbot
def chatbot_query(query):
    # Load recipe data and format a response
    recipe_names = recipes['Name'].to_list()
    recipes_str = "\n".join(recipe_names)
    
    # Create a prompt template with the available data
    prompt_template = """
    You are a helpful assistant that answers questions about recipes and nutrition.
    Here is a list of recipes:
    {recipes_list}
    
    Answer the following query: {query}
    """
    
    # Format the prompt with the data and the query
    prompt = prompt_template.format(recipes_list=recipes_str, query=query)
    
    # Use LangChain with OpenAI or another LLM to generate the response
    llm = OpenAI(model="text-davinci-003")  # You can change this to the LLM you are using
    prompt_template = PromptTemplate(input_variables=["query", "recipes_list"], template=prompt)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    response = chain.run(query=query, recipes_list=recipes_str)
    
    return response

# Streamlit Frontend UI for Chatbot Page
def user_input_form_page3():
    st.title("Chatbot: Ask Me About Recipes & Nutrition")

    user_query = st.text_input("Ask me anything about recipes or nutrition:")

    if user_query:
        response = chatbot_query(user_query)
        st.write("Answer: ", response)

# Main logic for the app with 3 pages
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Demographics & Activity", "Page 2: Nutrition Preferences", "Page 3: Chatbot"))

    user_preferences = {}

    # Page 1: User Demographics & Activity
    if page == "Page 1: Demographics & Activity":
        user_preferences = user_input_form_page1()

    # Page 2: Nutrition Preferences
    elif page == "Page 2: Nutrition Preferences":
        user_preferences = user_input_form_page2()

    # Page 3: Chatbot
    elif page == "Page 3: Chatbot":
        user_input_form_page3()

    # Add a button to get recommendations after both pages are filled
    if page != "Page 3: Chatbot" and st.button("Get Recommendations"):
        if user_preferences:
            top_recipes = recommend_recipes(user_preferences, recipes, top_n=5)
            st.write("### Top Recommended Recipes:")
            st.write(top_recipes[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']])

if __name__ == "__main__":
    main()
