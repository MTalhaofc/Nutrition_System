import streamlit as st
import pandas as pd
import numpy as np

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
def recommend_meals(tdee, goal):
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
    
    return recommended_recipes

# Streamlit Frontend UI for Page 1 (Meal Planning)
def user_input_form_page1():
    st.title('👤 User Demographics & Activity Level')

    # Collect user demographic and activity data
    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
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

    # Display recommended meals
    st.write(f"### Recommended Meals for Your Goal: {goal}")
    st.write(f"Meals that align with your target of {goal.lower()}:")

    st.write(recommended_recipes[['Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']])

    # Allow user to plan meals for the week
    user_meals = {}
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_times = ["Breakfast", "Lunch", "Dinner"]

    for day in days_of_week:
        user_meals[day] = {}
        for meal_time in meal_times:
            # Meal selection dropdown
            meal_options = recommended_recipes['Name'].tolist()
            selected_meal = st.selectbox(f"Select {meal_time} for {day}:", meal_options, key=f"{day}_{meal_time}")
            user_meals[day][meal_time] = selected_meal

    # Display the selected meal plan
    st.subheader("Your Weekly Meal Plan with Nutritional Information")
    meal_plan_data = []

    for day in days_of_week:
        for meal_time in meal_times:
            meal_name = user_meals[day][meal_time]
            meal_info = recipes[recipes['Name'] == meal_name].iloc[0]
            meal_plan_data.append({
                'Day': day,
                'Meal Time': meal_time,
                'Meal Name': meal_name,
                'Calories': meal_info['Calories'],
                'FatContent': meal_info['FatContent'],
                'ProteinContent': meal_info['ProteinContent'],
                'CarbohydrateContent': meal_info['CarbohydrateContent'],
            })

    meal_plan_df = pd.DataFrame(meal_plan_data)
    st.write(meal_plan_df)

    return user_meals

# Main function for the app
def main():
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Weekly Meal Plan", "Page 2: Nutrition Preferences"))

    # Page 1: Weekly Meal Planning
    if page == "Page 1: Weekly Meal Plan":
        user_meals = user_input_form_page1()

    # Additional pages and logic can be added here

if __name__ == "__main__":
    main()
