from hypergol import BaseData


class Token(BaseData):

    def __init__(
            self,
            i: int, startChar: int, endChar: int,
            depType: str, depHead: int, depLeftEdge: int, depRightEdge: int,
            posType: str, posFineType: str, lemma: str, text: str):
        self.i = i
        self.startChar = startChar
        self.endChar = endChar
        self.depType = depType
        self.depHead = depHead
        self.depLeftEdge = depLeftEdge
        self.depRightEdge = depRightEdge
        self.posType = posType
        self.posFineType = posFineType
        self.lemma = lemma
        self.text = text
