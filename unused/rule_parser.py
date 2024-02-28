from tokenizer import Token


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def consume(self, expected_type=None, expected_value=None):
        current = self.current_token()
        if (
            current is not None
            and (expected_type is None or current.type == expected_type)
            and (expected_value is None or current.value == expected_value)
        ):
            self.position += 1
            return current
        raise Exception(
            f"Expected token {expected_type} with value {expected_value}, but got {current}"
        )

    def parse(self):
        return self.expression()

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while (
            self.current_token()
            and self.current_token().type == "OPERATOR"
            and self.current_token().value == "OR"
        ):
            self.consume("OPERATOR", "OR")
            node = {"OR": [node, self.logical_and()]}
        return node

    def logical_and(self):
        # node = self.negation()
        while (
            self.current_token()
            and self.current_token().type == "OPERATOR"
            and self.current_token().value == "AND"
        ):
            self.consume("OPERATOR", "AND")
            node = self.negation()
            node = {"AND": [node, self.negation()]}
            return node
        node = self.negation()
        return node

    def negation(self):
        if (
            self.current_token()
            and self.current_token().type == "OPERATOR"
            and self.current_token().value == "NOT"
        ):
            self.consume("OPERATOR", "NOT")
            return {"NOT": self.primary()}
        return self.primary()

    def primary(self):
        token = self.current_token()
        if token and token.type == "PAREN" and token.value == "(":
            self.consume("PAREN", "(")
            node = self.expression()
            return node
        elif token and token.type == "PAREN" and token.value == ")":
            self.consume("PAREN", ")")
            node = self.expression()
            return node
        elif token and token.type in ["FUNCTION", "NUMBER"]:
            self.consume(token.type)
            return {"TOKEN": token.value}
        else:
            raise Exception("Unexpected token: " + str(token))


tokens = [
    Token("OPERATOR", "AND"),
    Token("PAREN", "("),
    Token("FUNCTION", "RULE"),
    Token("PAREN", "("),
    Token("FUNCTION", "BY_ID"),
    Token("PAREN", "("),
    Token("NUMBER", "3"),
    Token("PAREN", ")"),
    Token("PAREN", ")"),
    Token("COMMA", ","),
    Token("OPERATOR", "EXISTS"),
    Token("PAREN", "("),
    Token("PAREN", ")"),
    Token("PAREN", ")"),
]
parser = Parser(tokens)
parsed = parser.parse()
print(parsed)
