import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import random

# Load the datasets (replace with your paths or upload them)
recipes_path = 'recipes.csv'
reviews_path = 'reviews.csv'
recipes = pd.read_csv(recipes_path, on_bad_lines='skip')
reviews = pd.read_csv(reviews_path, on_bad_lines='skip')

# Preprocessing and Cleaning
nutritional_columns = ['RecipeId', 'Name', 'Calories', 'FatContent', 'ProteinContent', 'CarbohydrateContent']
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
            user_prefs[col] = recipes_df[col].median()
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

# Generate Weekly Meal Plan
def generate_weekly_meal_plan(calorie_needs, recipes_df):
    daily_calories = calorie_needs
    weekly_plan = []
    meals_per_day = 3
    for _ in range(7):
        daily_recipes = recipes_df[recipes_df['Calories'] <= daily_calories].sample(meals_per_day, replace=False)
    meals_per_day = 3  # Breakfast, Lunch, Dinner
    shuffled_recipes = recipes_df.sample(frac=1).reset_index(drop=True)  # Shuffle the entire recipes dataframe
    for _ in range(7):  # 7 days in a week
        daily_recipes = shuffled_recipes[shuffled_recipes['Calories'] <= daily_calories].head(meals_per_day)
        weekly_plan.append(daily_recipes)
    weekly_plan_df = pd.concat(weekly_plan)
    return weekly_plan_df
        shuffled_recipes = shuffled_recipes[~shuffled_recipes.index.isin(daily_recipes.index)]  # Remove used recipes
    return pd.concat(weekly_plan)

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
@@ -74,91 +65,57 @@ def calculate_tdee(bmr, activity_level):
    }
    return bmr * activity_multiplier[activity_level]

# Function to recommend meals based on TDEE and user goal
def recommend_meals(tdee, goal):
    if goal == "Gain Weight":
        target_calories = tdee + 500  # Surplus for weight gain
        calorie_range = (target_calories - 100, target_calories + 100)  # Allow a range around the target
        calorie_range = (target_calories - 100, target_calories + 100)
    elif goal == "Lose Weight":
        target_calories = tdee - 500  # Deficit for weight loss
        calorie_range = (target_calories - 100, target_calories + 100)
    else:
        target_calories = tdee  # Maintain weight
        calorie_range = (target_calories - 100, target_calories + 100)
    # Filter recipes based on the calorie range
    recommended_recipes = recipes[(recipes['Calories'] >= calorie_range[0]) & (recipes['Calories'] <= calorie_range[1])]
    return recommended_recipes
    return recommended_recipes.sample(n=5)

# Streamlit Frontend UI for Page 1 (User Details and Weekly Meal Plan)
def user_input_form_page1():
    st.title('User Details and Weekly Meal Plan')
    st.title('👤 User Demographics & Activity Level')

    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25)
    age = st.number_input('Enter your age:', min_value=0, max_value=120, value=25, step=1)
    gender = st.selectbox('Select your gender:', ['Male', 'Female', 'Other'])
    height = st.number_input('Enter your height (in cm):', min_value=50, max_value=250, value=170)
    weight = st.number_input('Enter your weight (in kg):', min_value=10, max_value=300, value=70)
    exercise = st.selectbox(
        'Select your activity level:', 
        ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extra Active']
    )
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
        
        # Print the columns to check what's available
        st.write("### Available Columns in Weekly Meal Plan:")
        st.write(weekly_meal_plan.columns)
        # Check if all the expected columns are available
        expected_columns = ['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']
        available_columns = [col for col in expected_columns if col in weekly_meal_plan.columns]
        if len(available_columns) != len(expected_columns):
            missing_columns = list(set(expected_columns) - set(available_columns))
            st.error(f"Missing columns in weekly meal plan: {', '.join(missing_columns)}")
        else:
            # If all expected columns are available, display the filtered DataFrame
            weekly_meal_plan = weekly_meal_plan[available_columns]
            st.write("### Your Weekly Meal Plan:")
            st.write(weekly_meal_plan)
        st.write("### Your Weekly Meal Plan:")
        st.write(weekly_meal_plan[['Name', 'Calories', 'ProteinContent', 'FatContent', 'CarbohydrateContent', 'SodiumContent', 'AverageRating']])

    return tdee

# Streamlit Frontend UI for Page 2 (Nutrition Preferences)
def user_input_form_page2():
    st.title('Nutrition Preferences')
    calories = st.slider('Max Calories per Meal:', 0, 1000, 500)
    protein = st.slider('Min Protein Content (g):', 0, 100, 20)
    fat = st.slider('Max Fat Content (g):', 0, 100, 15)
    carbs = st.slider('Max Carbohydrate Content (g):', 0, 100, 50)
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
# Main function for the app
def main():
    st.sidebar.title("Navigation")
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Choose a Page", ("Page 1: Weekly Meal Plan", "Page 2: Nutrition Preferences"))

    if page == "Page 1: Weekly Meal Plan":
        user_input_form_page1()
    elif page == "Page 2: Nutrition Preferences":
        user_input_form_page2()
