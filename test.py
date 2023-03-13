my_string = "This is a string with \\double backslashes"

if "\\" in my_string:

    split_string = my_string.split("\\")

    split_string = "/".join(split_string)

    print(split_string)
