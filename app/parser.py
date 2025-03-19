class QuoteProcessor:
    """
    Processes the input string using a shell-like state machine.
    Adjacent quoted and unquoted segments are concatenated.
    """

    @staticmethod
    def split_input(user_input: str):
        words = []
        current_word = ""
        i = 0
        n = len(user_input)

        while i < n:
            # Skip whitespace as a delimiter.
            if user_input[i].isspace():
                while i < n and user_input[i].isspace():
                    i += 1
                if current_word != "":
                    words.append(current_word)
                    current_word = ""
                continue

            char = user_input[i]

            # Process single-quoted strings (literal).
            if char == "'":
                i += 1
                while i < n and user_input[i] != "'":
                    current_word += user_input[i]
                    i += 1
                if i >= n:
                    raise ValueError("Unclosed single quote in input")
                i += 1  # Skip the closing quote.
                continue

            # Process double-quoted strings (with escape processing).
            if char == '"':
                i += 1
                while i < n and user_input[i] != '"':
                    if user_input[i] == "\\" and i + 1 < n:
                        next_char = user_input[i + 1]
                        if next_char in ['"', "\\", "$", "\n"]:
                            current_word += next_char
                            i += 2
                        else:
                            current_word += "\\" + next_char
                            i += 2
                    else:
                        current_word += user_input[i]
                        i += 1
                if i >= n:
                    raise ValueError("Unclosed double quote in input")
                i += 1  # Skip the closing quote.
                continue

            # Process backslash outside quotes.
            if char == "\\":
                if i + 1 < n:
                    current_word += user_input[i + 1]
                    i += 2
                else:
                    current_word += "\\"
                    i += 1
                continue

            # Append normal characters.
            current_word += char
            i += 1

        if current_word != "":
            words.append(current_word)
        return words