import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import random

# Load the recipes dataset (make sure this path points to your actual data)
recipes_path = 'recipes.csv'
reviews_path = 'reviews.csv'
recipes = pd.read_csv(recipes_path, on_bad_lines='skip')
reviews = pd.read_csv(reviews_path, on_bad_lines='skip')

# Preprocessing recipes (assuming columns like 'RecipeId', 'Name', 'Calories', 'FatContent', etc.)
nutritional_columns = ['RecipeId', 'Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']
recipes.columns = recipes.columns.str.strip()
recipes = recipes[nutritional_columns].dropna()

# Function to calculate BMR (Basal Metabolic Rate) using the Harris-Benedict equation
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
    meals_per_day = 3
    for _ in range(7):
        daily_recipes = recipes_df[recipes_df['Calories'] <= daily_calories].sample(meals_per_day, replace=False)
        weekly_plan.append(daily_recipes)
    return pd.concat(weekly_plan)
def calculate_bmr(age, weight, height, gender):
    if gender == 'Male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr

# Function to calculate TDEE (Total Daily Energy Expenditure)
def calculate_tdee(bmr, activity_level):
    activity_multiplier = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Extra Active': 1.9
    }
    return bmr * activity_multiplier[activity_level]

# Function to recommend meals based on TDEE and user goal
def recommend_meals(tdee, goal, num_meals=5):
    # Adjust the meal recommendations based on goal
def recommend_meals(tdee, goal):
    if goal == "Gain Weight":
        target_calories = tdee + 500  # Surplus for weight gain
        calorie_range = (target_calories - 100, target_calories + 100)  # Allow a range around the target
        target_calories = tdee + 500
        calorie_range = (target_calories - 100, target_calories + 100)
    elif goal == "Lose Weight":
        target_calories = tdee - 500  # Deficit for weight loss
        target_calories = tdee - 500
        calorie_range = (target_calories - 100, target_calories + 100)
    else:
        target_calories = tdee  # Maintain weight
        target_calories = tdee
        calorie_range = (target_calories - 100, target_calories + 100)
    # Filter recipes based on the calorie range
    recommended_recipes = recipes[(recipes['Calories'] >= calorie_range[0]) & (recipes['Calories'] <= calorie_range[1])]
    return recommended_recipes

    # Select a random sample of meals for display (ensuring variety)
    return recommended_recipes.sample(n=num_meals)
# Streamlit Frontend UI for Page 1 (Meal Planning)
def user_input_form_page1():
    st.title('User Details and Weekly Meal Plan')
    st.title('👤 User Demographics & Activity Level')

    # Collect user demographic and activity data
    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25, step=1)
    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170, step=1)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70, step=1)
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70)
    exercise = st.selectbox(
        'Select your activity level:', 
        ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extra Active']
    )
    goal = st.selectbox('Select your goal:', ['Maintain Weight', 'Gain Weight', 'Lose Weight'])

    # Calculate BMR and TDEE
    bmr = calculate_bmr(age, weight, height, gender)
    tdee = calculate_tdee(bmr, exercise)

    st.write(f"💡 Based on your input, your estimated daily calorie needs are: {int(tdee)} kcal.")
    # Recommend meals based on TDEE and goal
    recommended_recipes = recommend_meals(tdee, goal)
    # Display recommended meals for the goal
    st.write(f"### Recommended Meals for Your Goal: {goal}")
    st.write(f"Meals that align with your target of {goal.lower()}:")
    if st.button("Generate Weekly Meal Plan"):
        weekly_meal_plan = generate_weekly_meal_plan(tdee, recipes)
        st.write("### Your Weekly Meal Plan:")
        st.write(weekly_meal_plan[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']])

    # Display a list of recommended meals with nutritional information
    for idx, row in recommended_recipes.iterrows():
        st.write(f"**{row['Name']}**")
        st.write(f"Calories: {row['Calories']} kcal, Protein: {row['ProteinContent']} g, Fat: {row['FatContent']} g, Carbs: {row['CarbohydrateContent']} g")
        st.write("---")
    return tdee

    # Button to generate weekly meal plan
    if st.button("Generate Weekly Meal Plan"):
        # Randomly select meals for each day
        user_meals = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meal_times = ["Breakfast", "Lunch", "Dinner"]
        # Shuffle recipes and select a meal for each time slot
        meal_plan_data = []
        shuffled_recipes = recommended_recipes.sample(frac=1).reset_index(drop=True)
        for day in days_of_week:
            for meal_time in meal_times:
                selected_meal = shuffled_recipes.iloc[len(meal_plan_data) % len(shuffled_recipes)]
                meal_plan_data.append({
                    'Day': day,
                    'Meal Time': meal_time,
                    'Meal Name': selected_meal['Name'],
                    'Calories': selected_meal['Calories'],
                    'FatContent': selected_meal['FatContent'],
                    'ProteinContent': selected_meal['ProteinContent'],
                    'CarbohydrateContent': selected_meal['CarbohydrateContent'],
                })
        # Display the selected meal plan
        meal_plan_df = pd.DataFrame(meal_plan_data)
        st.write("### Your Weekly Meal Plan with Nutritional Information")
        st.write(meal_plan_df)
# Streamlit Frontend UI for Page 2 (Meal Recommendations)
def user_input_form_page2():
    st.title('🍽️ Get 5 Meal Recommendations')
    
    # Collect user input for nutrition preferences
    st.title('Nutrition Preferences')
    calories = st.slider('Max Calories per Meal:', 0, 1000, 500)
    protein = st.slider('Min Protein Content (g):', 0, 100, 20)
    fat = st.slider('Max Fat Content (g):', 0, 100, 15)
    carbs = st.slider('Max Carbohydrate Content (g):', 0, 100, 50)

    # Filter recipes based on the nutrition preferences
    filtered_recipes = recipes[
        (recipes['Calories'] <= calories) &
        (recipes['ProteinContent'] >= protein) &
        (recipes['FatContent'] <= fat) &
        (recipes['CarbohydrateContent'] <= carbs)
    ]
    # Button to get 5 meal recommendations
    if st.button("Get 5 Meal Recommendations"):
        if not filtered_recipes.empty:
            num_meals = min(5, len(filtered_recipes))  # Ensure we don't sample more than available
            recommended_meals = filtered_recipes.sample(n=num_meals)
            st.write("### Top 5 Recommended Meals:")
            st.write(recommended_meals[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent']])
        else:
            st.write("❌ No meals match your preferences. Try adjusting your inputs.")
# Main function for the app
    user_preferences = {
        'Calories': calories,
        'ProteinContent': protein,
        'FatContent': fat,
        'CarbohydrateContent': carbs
    }
    if st.button("Get Recipe Recommendations"):
        top_recipes = recommend_recipes(user_preferences, recipes, top_n=5)
        st.write("### Top Recommended Recipes:")
        st.write(top_recipes[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']])
def main():
    st.sidebar.title("📚 Navigation")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Weekly Meal Plan", "Page 2: Nutrition Preferences"))

    # Page 1: Weekly Meal Planning
    if page == "Page 1: Weekly Meal Plan":
        user_input_form_page1()

    # Page 2: Meal Recommendations
    elif page == "Page 2: Nutrition Preferences":
        user_input_form_page2()

if __name__ == "__main__":
    main()
