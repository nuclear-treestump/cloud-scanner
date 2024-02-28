from .decorator import autolog


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.position = 0
        self.tokens = []

    def advance(self):
        self.position += 1

    def add_token(self, type_, value):
        self.tokens.append(Token(type_, value))

    def tokenize(self):
        while self.position < len(self.text):
            char = self.text[self.position]

            if char.isspace():
                self.advance()
                continue

            elif char.isdigit():
                self.tokenize_number()

            elif char.isalpha():
                self.tokenize_identifier_or_keyword()

            elif char == "(" or char == ")":
                self.add_token("PAREN", char)
                self.advance()
            elif char == ",":
                self.add_token("COMMA", char)
                self.advance()

            else:
                raise Exception(f"Unknown character: {char}")

        return self.tokens

    def tokenize_number(self):
        number_str = ""
        while self.position < len(self.text) and self.text[self.position].isdigit():
            number_str += self.text[self.position]
            self.advance()
        self.add_token("NUMBER", int(number_str))

    def tokenize_identifier(self):
        identifier_str = ""
        while self.position < len(self.text) and (
            self.text[self.position].isalnum() or self.text[self.position] in ("_",)
        ):
            identifier_str += self.text[self.position]
            self.advance()

        self.add_token("IDENTIFIER", identifier_str)

    def tokenize_identifier_or_keyword(self):
        identifier_str = ""
        while self.position < len(self.text) and (
            self.text[self.position].isalnum() or self.text[self.position] in ("_",)
        ):
            identifier_str += self.text[self.position]
            self.advance()

        if identifier_str.upper() in (
            "AND",
            "OR",
            "NOT",
            "EXISTS",
            "IS_EMPTY",
            "RANDOM",
        ):
            self.add_token("OPERATOR", identifier_str.upper())
        elif identifier_str.upper() in ("RULE", "BY_ID", "BY_TABLE", "BY_COL"):
            self.add_token("FUNCTION", identifier_str.upper())
        else:
            self.add_token("IDENTIFIER", identifier_str)


if __name__ == "__main__":
    text = "AND(RULE(BY_ID(3)), EXISTS())"
    tokenizer = Tokenizer(text)
    tokens = tokenizer.tokenize()
    print(tokens)
