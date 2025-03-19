import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load dataset
recipes_path = 'recipes.csv'
recipes = pd.read_csv(recipes_path, on_bad_lines='skip')

# Select relevant columns
nutritional_columns = ['RecipeId', 'Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']
recipes = recipes[nutritional_columns].dropna()

# Normalize data
scaler = MinMaxScaler()
recipes[['Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']] = scaler.fit_transform(
    recipes[['Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']]
)

# BMR Calculation
def calculate_bmr(age, weight, height, gender):
    if gender.lower() == 'male':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

# TDEE Calculation
def calculate_tdee(bmr, activity_level):
    activity_multiplier = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Extra Active': 1.9
    }
    return bmr * activity_multiplier[activity_level]

# Recommend Meals
def recommend_meals(tdee, goal):
    target_calories = tdee + 500 if goal == "Gain Weight" else (tdee - 500 if goal == "Lose Weight" else tdee)
    target_values = np.array([[target_calories, target_calories, target_calories, target_calories]])
    target_scaled = scaler.transform(target_values)

    similarity_scores = cosine_similarity(target_scaled, recipes[['Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']])
    recommended_indices = similarity_scores[0].argsort()[-5:][::-1]
    return recipes.iloc[recommended_indices]

# Generate Weekly Meal Plan
def generate_weekly_meal_plan(recommended_recipes):
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

    return pd.DataFrame(meal_plan_data)

# Recommend Meals by Preferences
def recommend_meals_by_preferences(calories, protein, fat, carbs):
    user_preferences = np.array([[calories, fat, protein, carbs]])
    user_preferences_scaled = scaler.transform(user_preferences)
    
    similarity_scores = cosine_similarity(user_preferences_scaled, recipes[['Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']])
    
    recommended_indices = similarity_scores[0].argsort()[-5:][::-1]
    return recipes.iloc[recommended_indices]

# Command-line user interaction
def main():
    print("\n📢 Welcome to the Meal Recommendation System!\n")

    age = int(input("Enter your age: "))
    gender = input("Enter your gender (Male/Female): ").strip()
    height = float(input("Enter your height (in cm): "))
    weight = float(input("Enter your weight (in kg): "))

    print("\nActivity Levels:")
    print("1. Sedentary\n2. Lightly Active\n3. Moderately Active\n4. Very Active\n5. Extra Active")
    activity_options = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
    activity_level = activity_options[int(input("Choose your activity level (1-5): ")) - 1]

    print("\nGoals:")
    print("1. Maintain Weight\n2. Gain Weight\n3. Lose Weight")
    goal_options = ["Maintain Weight", "Gain Weight", "Lose Weight"]
    goal = goal_options[int(input("Choose your goal (1-3): ")) - 1]

    # Calculate TDEE
    bmr = calculate_bmr(age, weight, height, gender)
    tdee = calculate_tdee(bmr, activity_level)
    print(f"\n💡 Your estimated daily calorie needs: {int(tdee)} kcal.")

    # Recommend Meals
    recommended_recipes = recommend_meals(tdee, goal)
    print(f"\n🍽️ Recommended Meals for {goal}:")
    print(recommended_recipes[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent']])

    # Generate Weekly Meal Plan
    if input("\nWould you like to generate a weekly meal plan? (yes/no): ").strip().lower() == 'yes':
        meal_plan_df = generate_weekly_meal_plan(recommended_recipes)
        print("\n📅 Your Weekly Meal Plan:")
        print(meal_plan_df)

    # Meal Preferences-based Recommendations
    if input("\nWould you like meal recommendations based on specific nutrition preferences? (yes/no): ").strip().lower() == 'yes':
        calories = int(input("Max Calories per Meal: "))
        protein = int(input("Min Protein Content (g): "))
        fat = int(input("Max Fat Content (g): "))
        carbs = int(input("Max Carbohydrate Content (g): "))

        filtered_recipes = recipes[
            (recipes['Calories'] <= calories) &
            (recipes['ProteinContent'] >= protein) &
            (recipes['FatContent'] <= fat) &
            (recipes['CarbohydrateContent'] <= carbs)
        ]

        if not filtered_recipes.empty:
            recommended_meals = filtered_recipes.sample(n=5)
            print("\n🥗 Top 5 Recommended Meals:")
            print(recommended_meals[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent']])
        else:
            print("\n❌ No exact matches. Here are the closest 5 meal recommendations:")
            recommended_meals = recommend_meals_by_preferences(calories, protein, fat, carbs)
            print(recommended_meals[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent']])

if __name__ == "__main__":
    main()
