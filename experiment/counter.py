
def counter():
    # Define the file path
    file_path = 'irs/picozk_test.rel'

    # Initialize a variable to count lines
    line_count = 0

    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            line_count += 1

    # Print the total number of lines
    print(f"Total number of lines in the file: {line_count}")
