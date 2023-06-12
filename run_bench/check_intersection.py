import sys

def my_function():
    # Access the global variable within the function
    global my_global_variable
    print("The value of my_global_variable is:", my_global_variable)

if __name__ == "__main__":
    # Get the command-line arguments
    script_name, arg1 = sys.argv

    # Set the argument value as a global variable
    my_global_variable = arg1

    # Call the function
    my_function()
