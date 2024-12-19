import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import random

recipes_path = 'recipes.csv'
reviews_path = 'reviews.csv'
recipes = pd.read_csv(recipes_path, on_bad_lines='skip')
reviews = pd.read_csv(reviews_path, on_bad_lines='skip')

nutritional_columns = ['RecipeId', 'Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']
recipes.columns = recipes.columns.str.strip()
recipes = recipes[nutritional_columns].dropna()

average_ratings = reviews.groupby('RecipeId')['Rating'].mean().reset_index()
average_ratings.rename(columns={'Rating': 'AverageRating'}, inplace=True)
recipes = recipes.merge(average_ratings, on='RecipeId', how='left')
recipes['AverageRating'] = recipes['AverageRating'].fillna(0)

def recommend_recipes(user_prefs, recipes_df, top_n=5):
    nutrition_columns = ['Calories', 'FatContent', 'SodiumContent', 'CarbohydrateContent', 'ProteinContent']
    for col in nutrition_columns:
        recipes_df[col] = recipes_df[col].fillna(recipes_df[col].median())
    for col in nutrition_columns:
        if col not in user_prefs:
            user_prefs[col] = recipes_df[col].median()
    scaler = MinMaxScaler()
    recipes_scaled = recipes_df.copy()
    recipes_scaled[nutrition_columns] = scaler.fit_transform(recipes_df[nutrition_columns])
    user_vector = pd.DataFrame([user_prefs], columns=nutrition_columns)
    user_vector = scaler.transform(user_vector)
    similarity = cosine_similarity(user_vector, recipes_scaled[nutrition_columns])
    recipes_scaled['Similarity'] = similarity[0]
    recommendations = recipes_scaled.sort_values(by=['Similarity', 'AverageRating'], ascending=[False, False])
    return recommendations.head(top_n)

def generate_weekly_meal_plan(calorie_needs, recipes_df):
    daily_calories = calorie_needs
    weekly_plan = []
    meals_per_day = 3  # Breakfast, Lunch, Dinner
    shuffled_recipes = recipes_df.sample(frac=1).reset_index(drop=True)  # Shuffle the entire recipes dataframe

    for _ in range(7):  # 7 days in a week
        daily_recipes = shuffled_recipes[shuffled_recipes['Calories'] <= daily_calories].head(meals_per_day)
        weekly_plan.append(daily_recipes)
        shuffled_recipes = shuffled_recipes[~shuffled_recipes.index.isin(daily_recipes.index)]  # Remove used recipes

    return pd.concat(weekly_plan)

def calculate_bmr(age, weight, height, gender):
    if gender == 'Male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr

def calculate_tdee(bmr, activity_level):
    activity_multiplier = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Extra Active': 1.9
    }
    return bmr * activity_multiplier[activity_level]

def recommend_meals(tdee, goal):
    if goal == "Gain Weight":
        target_calories = tdee + 500  # Surplus for weight gain
        calorie_range = (target_calories - 100, target_calories + 100)
    elif goal == "Lose Weight":
        target_calories = tdee - 500  # Deficit for weight loss
        calorie_range = (target_calories - 100, target_calories + 100)
    else:
        target_calories = tdee  # Maintain weight
        calorie_range = (target_calories - 100, target_calories + 100)

    recommended_recipes = recipes[(recipes['Calories'] >= calorie_range[0]) & (recipes['Calories'] <= calorie_range[1])]
    return recommended_recipes.sample(n=5)

def user_input_form_page1():
    st.title('User Details and Weekly Meal Plan')
    st.title('👤 User Demographics & Activity Level')

    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25, step=1)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170, step=1)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70, step=1)
    exercise = st.selectbox('Select your activity level:', ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extra Active'])
    goal = st.selectbox('Select your goal:', ['Maintain Weight', 'Gain Weight', 'Lose Weight'])

    bmr = calculate_bmr(age, weight, height, gender)
    tdee = calculate_tdee(bmr, exercise)

    st.write(f"💡 Based on your input, your estimated daily calorie needs are: {int(tdee)} kcal.")
    
    recommended_recipes = recommend_meals(tdee, goal)
    st.write(f"### Recommended Meals for Your Goal: {goal}")
    st.write(f"Meals that align with your target of {goal.lower()}:")
    for idx, row in recommended_recipes.iterrows():
        st.write(f"**{row['Name']}**")
        st.write(f"Calories: {row['Calories']} kcal, Protein: {row['ProteinContent']} g, Fat: {row['FatContent']} g, Carbs: {row['CarbohydrateContent']} g")
        st.write("---")

    if st.button("Generate Weekly Meal Plan"):
        weekly_meal_plan = generate_weekly_meal_plan(tdee, recipes)
        st.write("### Your Weekly Meal Plan:")
        st.write(weekly_meal_plan[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']])

    return tdee

def main():
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Weekly Meal Plan", "Page 2: Nutrition Preferences"))

    if page == "Page 1: Weekly Meal Plan":
        user_input_form_page1()
    elif page == "Page 2: Nutrition Preferences":
        user_input_form_page2()

if __name__ == "__main__":
    main()
