# Parses xdv

from struct import unpack

opcodes = [("setchar", [], i) for i in range(128)]
opcodes += [
    ("parmop", [1], "setcode"),
    ("parmop", [2], "setcode"),
    ("parmop", [3], "setcode"),
    ("parmop", [-4], "setcode"),
    ("multiparm", [-4]*2, "setrule"),
    ("parmop", [1], "setcode"),
    ("parmop", [2], "setcode"),
    ("parmop", [3], "setcode"),
    ("parmop", [-4], "setcode"),
    ("multiparm", [-4]*2, "setrule"),
    ("simple", [], "nop"),
    ("bop", [4]*11, "bop"),
    ("simple", [], "eop"),       # code 140
    ("simple", [], "push"),
    ("simple", [], "pop"),
    ("parmop", [-1], "right"),
    ("parmop", [-2], "right"),
    ("parmop", [-3], "right"),
    ("parmop", [-4], "right"),
    ("simple", [], "w"),
    ("parmop", [-1], "w"),
    ("parmop", [-2], "w"),
    ("parmop", [-3], "w"),         # code 150
    ("parmop", [-4], "w"),
    ("simple", [], "x"),
    ("parmop", [-1], "x"),
    ("parmop", [-2], "x"),
    ("parmop", [-3], "x"),
    ("parmop", [-4], "x"),
    ("parmop", [-1], "down"),
    ("parmop", [-2], "down"),
    ("parmop", [-3], "down"),
    ("parmop", [-4], "down"),
    ("simple", [], "y"),
    ("parmop", [-1], "y"),
    ("parmop", [-2], "y"),
    ("parmop", [-3], "y"),
    ("parmop", [-4], "y"),
    ("simple", [], "z"),
    ("parmop", [-1], "z"),
    ("parmop", [-2], "z"),
    ("parmop", [-3], "z"),
    ("parmop", [-4], "z")]         # code 170
opcodes += [("font", [], i) for i in range(64)]
opcodes += [
    ("font", [1], None),
    ("font", [2], None),
    ("font", [3], None),
    ("font", [4], None),
    ("xxx", [1], None),
    ("xxx", [2], None),
    ("xxx", [3], None),
    ("xxx", [4], None),
    ("fontdef", [1, 4, 4, 4, 1, 1], None),
    ("fontdef", [2, 4, 4, 4, 1, 1], None),
    ("fontdef", [3, 4, 4, 4, 1, 1], None),
    ("fontdef", [4, 4, 4, 4, 1, 1], None),
    ("pre", [1, 4, 4, 4, 1], None),
    ("multiparm", [4]*6 + [2,2], "post"),
    ("multiparm", [4, 1], "postpost"),
    ("unknown", [], None),   # code 250
    ("xpic", [1, 4, 4, 4, 4, 4, 4, 2, 2], None),
    ("xfontdef", [4, 4, 2], None),
    ("xglyphs", [], 1),
    ("xglyphs", [], 0),
    ("parmop", [1], "direction")]

packings = ("bhxi", "BHxI")

class XDVi:
    def __init__(self, fname, diffable=False):
        self.fonts = {}
        self.fname = fname
        self.diffable = diffable
        self.pageno = 0
        self.file = None

    def __enter__(self):
        self.file = open(self.fname, "rb")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.file is not None:
            self.file.close()
            self.file = None

    def __iter__(self):
        return self

    def __next__(self):
        op = self.readval(1, uint=True)
        opc = opcodes[op]
        data = [self.readval((x if x>0 else -x), uint=x>0) for x in opc[1]]
        return (opc, data)

    def readbytes(self, num):
        return self.file.read(num)

    def readval(self, size, uint=False):
        d = self.readbytes(size)
        if size == 3:
            if uint:
                s = unpack(">"+packings[1][1]+packings[1][0], d)
                res = s[0] * 256 + s[1]
            else:
                s = unpack(">"+packings[0][1]+packings[1][0], d)
                res = s[0] * 256 + (s[1] if s[0] > 0 else -s[1])
        else:
            res = unpack(">"+packings[1 if uint else 0][size-1], d)[0]
        return res

    def parse(self):
        selfopen = False
        if self.file is None:
            selfopen = True
            self.__enter__()
        for (opc, data) in self:
            getattr(self, opc[0])(op, lastparm, data)
            if opc[2] == "postpost":
                break
        if selfopen:
            self.__exit__()
            self.file = None

    def out(self, txt):
        # print(("pg[{}] ".format(self.pageno) + txt).encode("utf-8"))
        pass

    def setchar(self, opcode, parm, data):
        # self.out("setchar({})".format(opcode))
        pass

    def multiparm(self, opcode, parm, data):
        # self.out("{}({}) {}".format(parm, opcode, data))
        pass

    def parmop(self, opcode, parm, data):
        # self.out("{}({}) [{}]".format(parm, opcode, data[0]))
        pass

    def simple(self, opcode, parm, data):
        # self.out("{}".format(parm))
        pass

    def bop(self, opcode, parm, data):
        self.pageno = data[0]
        # self.out("{}({}) [{}]".format(parm, opcode, data[0]))

    def font(self, opcode, parm, data):
        if parm is not None:
            data = [parm]
        # self.out("font [{:04x}]".format(self.fonts[data[0]][0]))

    def xxx(self, opcode, parm, data):
        txt = self.readbytes(data[0])
        # self.out('special({}) "{}"'.format(opcode, txt.decode("utf-8")))

    def fontdef(self, opcode, parm, data):
        (k, c, s, d, a, l) = data
        n = self.readbytes(a+l).decode("utf-8")

    def pre(self, opcode, parm, data):
        (i, n, d, m, k) = data
        x = self.readbytes(k)
        # self.out("pre num={}, den={}, mag={} {}".format(n, d, m, x))
        # the k to c mapping may vary across 'identical' files
        # self.out("fontdef({}) checksum={:04x} sf={:f} name=\"{}\"".format(opcode, c, s / 1000. / d, n))
        self.fonts[k] = (c, n)

    def xfontdef(self, opcode, parm, data):
        (k, points, flags) = data
        plen = self.readval(1, uint=True)
        font_name = self.readbytes(plen).decode("utf-8")
        if self.diffable:
            font_name = os.path.basename(font_name)
        ident = self.readval(4)
        color = self.readval(4) if flags & 0x200 else 0xFFFFFFFF
        if flags & 0x800:       # variations
            nvars = self.readval(2)
            variations = [self.readval(4) for i in range(nvars)]
        else:
            variations = []
        ext = self.readval(4) if flags & 0x1000 else 0
        slant = self.readval(4) if flags & 0x2000 else 0
        embolden = self.readval(4) if flags & 0x4000 else 0
        self.fonts[k]=(ident, font_name)
        # self.out('xfontdef[{}] "{}", size={}, flags={:04X}, color={:08X}, vars={}, ext={}, slant={}, embolden={}'.format(
        #          ident, font_name, points, flags, color, variations, ext, slant, embolden))

    def xglyphs(self, opcode, parm, data):
        width = self.readval(4)
        slen = self.readval(2, uint=True)
        if parm:
            pos = [(self.readval(4), self.readval(4)) for i in range(slen)]
        else:
            pos = [(self.readval(4), 0) for i in range(slen)]
        glyphs = [self.readval(2) for i in range(slen)]
        # res = ["{}@({},{})".format(glyphs[i], *pos[i]) for i in range(slen)]
        # self.out("xglyphs: {}".format(res))

    def xpic(self, opcode, parm, data):
        box = data.pop(0)
        length = data.pop()
        pageno = data.pop()
        matrix = data[:]
        # path = self.readbytes(length).decode("utf-8")
        # self.out('xpic "{}"@{} pageno={}, box={}'.format(path, matrix, pageno, box))

