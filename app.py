import streamlit as st
import pandas as pd
import random

# Load the recipes dataset (make sure this path points to your actual data)
recipes_path = 'recipes.csv'
recipes = pd.read_csv(recipes_path, on_bad_lines='skip')

# Preprocessing recipes (assuming columns like 'RecipeId', 'Name', 'Calories', 'FatContent', etc.)
nutritional_columns = ['RecipeId', 'Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']
recipes = recipes[nutritional_columns].dropna()

# Function to calculate BMR (Basal Metabolic Rate) using the Harris-Benedict equation
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
    if goal == "Gain Weight":
        target_calories = tdee + 500  # Surplus for weight gain
        calorie_range = (target_calories - 100, target_calories + 100)  # Allow a range around the target
    elif goal == "Lose Weight":
        target_calories = tdee - 500  # Deficit for weight loss
        calorie_range = (target_calories - 100, target_calories + 100)
    else:
        target_calories = tdee  # Maintain weight
        calorie_range = (target_calories - 100, target_calories + 100)

    # Filter recipes based on the calorie range
    recommended_recipes = recipes[(recipes['Calories'] >= calorie_range[0]) & (recipes['Calories'] <= calorie_range[1])]

    # Select a random sample of meals for display (ensuring variety)
    return recommended_recipes.sample(n=num_meals)

# Streamlit Frontend UI for Page 1 (Meal Planning)
def user_input_form_page1():
    st.title('👤 User Demographics & Activity Level')

    # Collect user demographic and activity data
    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25, step=1)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170, step=1)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70, step=1)
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

    # Display a list of recommended meals with nutritional information
    for idx, row in recommended_recipes.iterrows():
        st.write(f"**{row['Name']}**")
        st.write(f"Calories: {row['Calories']} kcal, Protein: {row['ProteinContent']} g, Fat: {row['FatContent']} g, Carbs: {row['CarbohydrateContent']} g")
        st.write("---")

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
def main():
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Weekly Meal Plan", "Page 2: Nutrition Preferences"))

    # Page 1: Weekly Meal Planning
    if page == "Page 1: Weekly Meal Plan":
        user_input_form_page1()

    # Page 2: Meal Recommendations
    elif page == "Page 2: Nutrition Preferences":
        user_input_form_page2()

if __name__ == "__main__":
    main()
