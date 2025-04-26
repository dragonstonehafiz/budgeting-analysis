from openai import OpenAI
from tqdm import tqdm
import pandas as pd

def generate_categories(client: OpenAI, items: list) -> str:
    items_string = "\n".join(items.tolist())
    
    system_prompt = f"""
    You are a helpful assistant that creates practical and intuitive categories for personal purchase items.
    Your task is to group items into a small set of consistent, human-friendly categories that would make sense for budgeting or spending review. 
    You should be concise, avoid overly specific categories, and use everyday language.
    """

    user_prompt = f"""
    I have a list of items from my personal purchase history. Please group them into intuitive, non-overlapping spending categories. Your task is to:

    1. Identify and list a practical set of categories to organize these purchases. Keep the number under 10.
    2. Make sure the categories are distinct — avoid overlapping groups. For example:
    - Separate 'Gaming' (video games and in-game purchases) from 'Digital Subscriptions' (e.g. software, music services, cloud apps).
    - Use 'Apparel' only for wearable clothing — do not include accessories like bags or watches unless they are strictly clothing-related.
    - Combine 'Fitness', 'Health', and 'Personal Care' into a single category.
    - Use 'Music & Soundtracks' for both physical and digital music/soundtrack purchases. Music streaming subscriptions should go under 'Digital Subscriptions'.
    - Separate 'Books' into its own category — distinct from 'Entertainment' or 'Education'.
    - Manga and light novels should be included under the 'Books & Literature' category.
    - Group items clearly intended for collection (e.g. enamel pins, commemorative coins, special edition memorabilia) into a category called 'Collectibles'.
    - Include artbooks that are themed around games, movies, or anime as part of the 'Collectibles' category (not 'Books').
    3. **Do not invent or include categories that are not clearly represented by actual examples from the item list.**

    For each category you do create, provide:
    - A short explanation of what kinds of items belong in it
    - Exactly 3 example items from my list that belong in that category

    Here is the list of items:

    {items_string}

    Please organize the response in this format:

    Category Details:
    - **[Category Name]**: [short explanation]  
    Example items (Only 3): [item a], [item b], [item c]
    ...
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=1000)
    
    return response.choices[0].message.content


def create_category_string(metadata_filepath = "metadata/categories.csv"):
    metadata_df = pd.read_csv(metadata_filepath, encoding="utf-8")
    
    categories = []
    for index, row in metadata_df.iterrows():
        name = row["Category"]
        description = row["Description"]
        example = row["Examples"]
        
        category_string = f"""**{name}**: {description}
        Example items (Only 3): {example}"""
        categories.append(category_string)
        
    category_string = "\n".join(categories)
    
    return category_string


def classify_item(client: OpenAI, item_name: str, category_string: str) -> str:
    system_prompt = f"""
    You are a helpful assistant that classifies purchase items into exactly one of a predefined set of spending categories. 
    Each category includes a name, a short description, and example items. 
    Use these references to make a precise and consistent classification. 
    Return only the name of the most appropriate category — do not invent new categories or output anything else.
    """

    user_prompt = f"""
    You are given a list of predefined spending categories, each with a description and example items.

    Your task is to classify the following purchase item into exactly one of these categories.

    Item: {item_name}

    Categories:
    {category_string}

    Instructions:
    - Choose only **one** category from the list above.
    - Your answer must exactly match the name of one of the listed categories.
    - Do not explain your choice or include any additional text.
    - Do not create new categories.

    Return only the category name that best fits the item.
    """
    
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.1,
    max_tokens=100)
    
    return response.choices[0].message.content

def classify_items_in_df(client: OpenAI, df: pd.DataFrame, category_string: str, output_path: str = "dataframe") -> pd.DataFrame:
    df = df.copy()
    categories = []
        
    for index, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {output_path}", unit="row"):
        item_name = row["Item"]
        category = classify_item(client, item_name, category_string)
        categories.append(category)
        
    df["Category"] = categories
    return df
