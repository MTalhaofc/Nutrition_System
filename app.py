import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

# Recommendation System
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

# Streamlit Frontend UI for Page 1 (Demographic and Activity)
def user_input_form_page1():
    st.title('User Demographics & Activity Level')

    # Collect user demographic and activity data
    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70)
    exercise = st.selectbox(
        'Select your activity level:', 
        ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extra Active']
    )

    # Calculate estimated daily calorie needs based on user input (simplified Harris-Benedict formula)
    if gender == 'Male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    activity_multiplier = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Extra Active': 1.9
    }

    daily_calorie_needs = bmr * activity_multiplier[exercise]
    st.write(f"Based on your input, your estimated daily calorie needs are: {int(daily_calorie_needs)} kcal.")

    # Update user preferences with demographic information
    user_preferences = {
        'EstimatedCalories': daily_calorie_needs,
        'Age': age,
        'Height': height,
        'Weight': weight,
        'Gender': gender,
        'ActivityLevel': exercise
    }
    
    return user_preferences

# Streamlit Frontend UI for Page 2 (Nutrition Preferences)
def user_input_form_page2():
    st.title('Nutrition Preferences')

    # Collect user input for preferences
    calories = st.slider('Max Calories:', 0, 1000, 500)
    protein = st.slider('Min Protein Content (g):', 0, 100, 20)
    fat = st.slider('Max Fat Content (g):', 0, 100, 15)
    carbs = st.slider('Max Carbohydrate Content (g):', 0, 100, 50)

    # Update user preferences with nutrition data
    user_preferences = {
        'Calories': calories,
        'ProteinContent': protein,
        'FatContent': fat,
        'CarbohydrateContent': carbs
    }
    
    return user_preferences

# Main logic for the app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Demographics & Activity", "Page 2: Nutrition Preferences"))

    user_preferences = {}

    # Page 1: User Demographics & Activity
    if page == "Page 1: Demographics & Activity":
        user_preferences = user_input_form_page1()

    # Page 2: Nutrition Preferences
    elif page == "Page 2: Nutrition Preferences":
        user_preferences = user_input_form_page2()

    # Add a button to get recommendations after both pages are filled
    if st.button("Get Recommendations"):
        if user_preferences:
            top_recipes = recommend_recipes(user_preferences, recipes, top_n=5)
            st.write("### Top Recommended Recipes:")
            st.write(top_recipes[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']])

if __name__ == "__main__":
    main()
