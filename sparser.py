"""
Smalltalk statement parser
"""

class ParseError(Exception): pass

class ParseStatementList(object):
    """
    Represent a list of statements.
    """
    def __init__(self, x):
        self.data = x

class ParseStatement(object):
    """
    Represent a single statement
    """
    def __init__(self, x):
        self.data = x

class ParseExecStatement(ParseStatement):
    """
    Represent a statement with no return
    or assign.
    """
    pass

class ParseReturnStatement(ParseStatement):
    """
    Represent a return statement
    """
    pass

class ParseAssignStatement(ParseStatement):
    """
    Represent an assignment statement
    """
    def __init__(self, var, x):
        super().__init__(x)
        self.var = var

class ParseMessage(object):
    """
    Represent a message to a receiver
    """
    def __init__(self, recv):
        self.recv = recv

class ParseUnaryMessage(ParseMessage):
    """
    Represent a unary message
    """
    def __init__(self, recv, name):
        super().__init__(recv)
        self.name = name
        
class ParseExprMessage(ParseMessage):
    """
    Represent a binary expression message
    """
    def __init__(self, recv, name, send):
        super().__init__(recv)
        self.name = name
        self.send = send
        
class ParseArgumentMessage(ParseMessage):
    """
    Represent an argument list message
    """
    def __init__(self, recv, args):
        super().__init__(recv)
        self.args = args
        
class ParseMessageArg(object):
    """
    Represent a message argument/value pair
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ParseLiteral(object):
    """
    Represent a literal value
    """
    def __init__(self, x):
        self.value = x
        
class ParseLiteralString(ParseLiteral):
    """
    Represent a 'string literal' value
    """
    pass
        
class ParseLiteralBlock(ParseLiteral):
    """
    Represent a [block] value
    """
    pass
 
class ParseError(Exception):
    """
    Signal a parser error
    """

class Parser(object):
    """
    Statement parser implementation
    """
    
    # expression filters
    EXPR_ASSIGNMENT     = 1
    EXPR_GREATER        = 2
    EXPR_BINOP          = 4
    EXPR_KEYWORD        = 8
    EXPR_CASCADE        = 16
    EXPR_CASCADED       = EXPR_BINOP | EXPR_KEYWORD
    EXPR_ANY            = 31
    
    def __init__(self, lexer):
        """
        Create parser instance
        """
        self._lex = lexer
        self._la = [None] * 4
        self._la_first = 0
        self._la_size = 0
    
    def reset(self):
        """
        Reset the parser state
        """
        Parser.__init__(self, self._lex)
        self.lookahead(1)
        
    def lookahead(self, n):
        """
        Fill lookahead with new tokens
        """
        while self._la_size < n:
            i = (self._la_first + self._la_size) % 4
            self._la[i] = self._lex.token()
            self._la_size += 1
            #print("<%d>: %s" % (i, self._la[i]))

    def consume(self, n):
        """
        Drop tokens from lookahead
        """
        self._la_first = (self._la_first + n) % 4
        self._la_size -= n
        
    def lex(self):
        """
        Drop current token and get next
        """
        self.consume(1)
        self.lookahead(1)
        
    def token(self, n):
        """
        Get token type from lookahead
        """
        i = (self._la_first + n) % 4
        t = self._la[i]
        if t is None:
            return None
        return t.type
        
    def val(self, n):
        """
        Get token value from lookahead
        """
        i = (self._la_first + n) % 4
        t = self._la[i]
        if t is None:
            return None
        return t.value
        
    def lex_skip_if(self, tok):
        """
        Look for token and eat it if present.
        Returns True if token found, False otherwise.
        """
        t0 = self.token(0)
        if t0 != tok:
            return False
        else:
            self.lex()
            return True
            
    def lex_skip_manditory(self, tok):
        """
        Look for and eat token, otherwise exception
        """
        if self.token(0) != tok:
            raise ParseError("expected token %s" % tok)
        else:
            self.lex()
        
    def parse_statements(self):
        """
        Parse a list of statements separated by '.'
        """
        sList = []
        while True:
            carFlag = self.lex_skip_if("CARET")
            s = self.parse_expr(self.EXPR_ANY)
            if carFlag:
                sList.append(ParseReturnStatement(s))
            else:
                sList.append(s)
            if (not self.lex_skip_if("PERIOD")) or carFlag:
                break
        return ParseStatementList(sList)
        
    def parse_expr(self, kind):
        """
        Parse a general expression
        """
        assign = None
        while True:
            if self.token(0) != "IDENT":
                node = self.parse_primary()
                break
            else:
                node = ParseLiteral(self.val(0))
                self.lex()
                if self.lex_skip_if("ASSIGN"):
                    assign = node
                else:
                    break
                    
        node = self.parse_message(node, kind)
        
        if assign is not None:
            return ParseAssignStatement(assign, ParseExecStatement(node))
        else:
            return ParseExecStatement(node)
        
    def parse_primary(self):
        """
        Parse an isolated token
        """
        node = None
        tok = self.token(0)
        if      (tok == "IDENT") or \
                (tok == "DECNUMBER"):
            node = ParseLiteral(self.val(0))
            self.lex()
        elif tok == "LPARENS":
            self.lex()
            node = self.parse_expr(self.EXPR_ANY)
            self.lex_skip_manditory("RPARENS")
        return node
        
    def parse_message(self, recv, kind):
        """
        Parse a message send expression
        """
        node = recv
        n = 0
        while True:
            tok = self.token(0)
            if tok == "IDENT":
                node = self.parse_message_unary(node, kind)
            elif tok == "OPERATOR":
                if not (kind & self.EXPR_BINOP):
                    return node
                node = self.parse_message_binary(node, kind)
            elif tok == "MESSAGEARG":
                if not (kind & self.EXPR_KEYWORD):
                    return node
                node = self.parse_message_keyword(node, kind)
            else:
                return node
            n += 1
            if n > 1000:
                raise ParseError("parse msg overflow")
                
    def parse_message_unary(self, recv, kind):
        """
        Parse a unary message
        """
        sel = self.val(0)
        self.lex()
        return ParseUnaryMessage(recv, sel)
    
    def parse_message_binary(self, recv, kind):
        """
        Parse a binary expression message
        """
        sel = self.val(0)
        self.lex()
        node = self.parse_expr(kind & ~self.EXPR_BINOP)
        return ParseExprMessage(ParseExecStatement(recv), sel, node)
        
    def parse_message_keyword(self, recv, kind):
        """
        Parse a keyword list message
        """
        aList = []
        while True:
            name = self.val(0)
            self.lex()
            arg = self.parse_expr(kind & ~self.EXPR_KEYWORD)
            aList.append(ParseMessageArg(name, arg))
            if self.token(0) != "MESSAGEARG":
                break
        return ParseArgumentMessage(ParseExecStatement(recv), aList)
            