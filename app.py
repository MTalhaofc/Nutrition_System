import streamlit as st
import pandas as pd


recipes_path = 'recipes.csv'
recipes = pd.read_csv(recipes_path, on_bad_lines='skip')

nutritional_columns = ['RecipeId', 'Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']
recipes = recipes[nutritional_columns].dropna()

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
        target_calories = tdee + 500
        calorie_range = (target_calories - 100, target_calories + 100)
    elif goal == "Lose Weight":
        target_calories = tdee - 500
        calorie_range = (target_calories - 100, target_calories + 100)
    else:
        target_calories = tdee
        calorie_range = (target_calories - 100, target_calories + 100)

    recommended_recipes = recipes[(recipes['Calories'] >= calorie_range[0]) & (recipes['Calories'] <= calorie_range[1])]
    return recommended_recipes

def user_input_form_page1():
    st.title('👤 User Demographics & Activity Level')

    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70)
    exercise = st.selectbox(
        'Select your activity level:', 
        ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extra Active']
    )
    goal = st.selectbox('Select your goal:', ['Maintain Weight', 'Gain Weight', 'Lose Weight'])

    bmr = calculate_bmr(age, weight, height, gender)
    tdee = calculate_tdee(bmr, exercise)

    st.write(f"💡 Based on your input, your estimated daily calorie needs are: {int(tdee)} kcal.")

    recommended_recipes = recommend_meals(tdee, goal)

    st.write(f"### Recommended Meals for Your Goal: {goal}")
    st.write(f"Meals that align with your target of {goal.lower()}:")

    if st.button("Generate Weekly Meal Plan"):
        user_meals = {}
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        meal_times = ["Breakfast", "Lunch", "Dinner"]

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

        meal_plan_df = pd.DataFrame(meal_plan_data)
        st.write("### Your Weekly Meal Plan with Nutritional Information")
        st.write(meal_plan_df)

    return recommended_recipes

def user_input_form_page2():
    st.title('🍽️ Get 5 Meal Recommendations')
    
    calories = st.slider('Max Calories per Meal:', 0, 1000, 500)
    protein = st.slider('Min Protein Content (g):', 0, 100, 20)
    fat = st.slider('Max Fat Content (g):', 0, 100, 15)
    carbs = st.slider('Max Carbohydrate Content (g):', 0, 100, 50)

    filtered_recipes = recipes[
        (recipes['Calories'] <= calories) &
        (recipes['ProteinContent'] >= protein) &
        (recipes['FatContent'] <= fat) &
        (recipes['CarbohydrateContent'] <= carbs)
    ]

    if st.button("Get 5 Meal Recommendations"):
        if not filtered_recipes.empty:
            num_meals = min(5, len(filtered_recipes))
            recommended_meals = filtered_recipes.sample(n=num_meals)
            st.write("### Top 5 Recommended Meals:")
            st.write(recommended_meals[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent']])
        else:
            st.write("❌ No meals match your preferences. Try adjusting your inputs.")

def main():
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Weekly Meal Plan", "Page 2: Nutrition Preferences"))

    if page == "Page 1: Weekly Meal Plan":
        user_input_form_page1()

    elif page == "Page 2: Nutrition Preferences":
        user_input_form_page2()

if __name__ == "__main__":
    main()
