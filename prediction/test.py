import os

# Get the base directory of the current file (ml_model.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up (to the root of the 'prediction' app)
parent_dir = os.path.dirname(current_dir)

# Create full path to 'test.py'
test_file_path = os.path.join(parent_dir, 'test.py')

print("Absolute path to test.py:", test_file_path)
