# core/controller.py
class PieceController:
    def __init__(self, board: BoardProtocol, rules: RuleSet, shapes: ShapeSet):
        self.board, self.rules, self.shapes = board, rules, shapes

    def try_move(self, piece, dx=0, dy=0):
        test = piece.moved(dx, dy)
        return test if self.board.valid(test) else None

    def try_rotate(self, piece, dr):
        cand = piece.rotated(dr)
        for dx in self.rules.kick_table(cand.kind, piece.rot, cand.rot):
            test = cand.moved(dx, 0)
            if self.board.valid(test):
                return test
        return None

    def hard_drop_and_lock(self, piece, level):
        dy = self.board.drop_distance(piece)
        dropped = piece.moved(0, dy)
        cleared = self.board.lock(dropped)
        score = self.rules.score(cleared, level) if cleared else 0
        return dropped, cleared, score
