import random
from pathlib import Path
import pandas as pd
from flask import Flask, request, jsonify
from flask import send_from_directory


app = Flask(__name__)

import os

@app.route("/")
def serve_ui():
    directory = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(directory=directory, filename="challenge_ui.html")

def read_csv_file(file_path: Path) -> pd.DataFrame:
    """
    Read the CSV file and return the content as a pandas DataFrame.
    """
    df = pd.read_csv(file_path)
    return df

def create_equation() -> (str, int):
    """
    Create an equation in the format "x + y = a + b" with randomly chosen 3-digit numbers.
    Return the equation and the index of the missing number.
    """
    numbers = [random.randint(100, 999) for _ in range(4)]
    missing_index = random.randint(0, 3)
    numbers[missing_index] = "?"
    equation = f"{numbers[0]} + {numbers[1]} = {numbers[2]} + {numbers[3]}"
    return equation, missing_index

def get_random_reward_rows(df: pd.DataFrame, num_rows: int) -> pd.DataFrame:
    """
    Get random reward rows from the DataFrame where the color_name is not #f7f7f7.
    """
    non_white_rows = df[df["color_name"] != "#f7f7f7"]
    reward_rows = non_white_rows.sample(n=num_rows)
    return reward_rows

@app.route("/challenge", methods=["POST"])
def challenge():
    base_folder = Path("/Users/senthilgandhi/Dropbox/parent/workspace/pixel_puzzle_math")
    file_path = base_folder / "color_mapping.csv"
    data = request.json
    coordinates = data["coordinates"]
    data_frame = read_csv_file(file_path)

    equation, missing_index = create_equation()
    response = {
        "coordinates": coordinates,
        "equation": equation,
        "missing_index": missing_index
    }
    return jsonify(response)

@app.route("/submit", methods=["POST"])
def submit_answer():
    data = request.json
    user_input = int(data["user_input"])
    equation = data["equation"]
    missing_index = int(data["missing_index"])
    base_folder = Path("/Users/senthilgandhi/Dropbox/parent/workspace/pixel_puzzle_math")
    file_path = base_folder / "color_mapping.csv"
    data_frame = read_csv_file(file_path)

    # Calculate the correct answer
    import re

    number_strings = re.findall(r'\d+|\?', equation)
    numbers = [int(num) if num != '?' else '?' for num in number_strings]
    print("numbers", numbers)
    numbers.insert(missing_index, '?')
    if missing_index == 0:
        correct_answer = numbers[2] + numbers[3] - numbers[1]
    elif missing_index == 1:
        correct_answer = numbers[2] + numbers[3] - numbers[0]
    elif missing_index == 2:
        correct_answer = numbers[0] + numbers[1] - numbers[3]
    else:
        correct_answer = numbers[0] + numbers[1] - numbers[2]

    print(f"Correct answer: {correct_answer}")

    if user_input == correct_answer:
        reward_rows = get_random_reward_rows(data_frame, 10)
        response = {
            "message": "Congratulations! Here is your reward",
            "reward": reward_rows.to_dict(orient="records")
        }
    else:
        response = {
            "message": "Sorry, try again"
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
