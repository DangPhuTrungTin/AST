from MPVisitor import MPVisitor
from MPParser import MPParser
from AST import *

class ASTGeneration(MPVisitor):
    def visitProgram(self,ctx:MPParser.ProgramContext):
        from itertools import chain
        A=[self.visit(x) for x in ctx.body()]
        B=list(chain.from_iterable(A))
        return Program(B)
    def visitFuncdecl(self,ctx:MPParser.FuncdeclContext):
        local,cpstmt = self.visit(ctx.vardecl()) if ctx.vardecl() else [],self.visit(ctx.compoundstatement())
        return FuncDecl(Id(ctx.ID().getText()),
                        self.visit(ctx.pardec()),
                        local,
                        cpstmt,
                        self.visit(ctx.mtype()))

    def visitProcdecl(self,ctx:MPParser.ProcdeclContext):
        local,cpstmt =self.visit(ctx.vardecl()) if ctx.vardecl() else [] ,self.visit(ctx.compoundstatement())
        return FuncDecl(Id(ctx.ID().getText()),
                        self.visit(ctx.pardec()),
                        local,
                        cpstmt)

    def visitBody(self,ctx:MPParser.BodyContext):
        if ctx.vardecl():
            return self.visit(ctx.vardecl())
        elif ctx.funcdecl():
            return [self.visit(ctx.funcdecl())]
        else:
            return [self.visit(ctx.procdecl())]
    def visitVardecl(self, ctx:MPParser.VardeclContext):
        return self.visit(ctx.listofvardec())
    def visitCompoundstatement(self, ctx:MPParser.CompoundstatementContext):
        from itertools import chain
        A=[self.visit(x) for x in ctx.statement()] if ctx.statement() else []
        return list(chain.from_iterable(A))
    def visitStatement(self, ctx:MPParser.StatementContext):
        if ctx.assignmentstatement():
            return self.visit(ctx.assignmentstatement())
        elif ctx.ifstatement():
            return [self.visit(ctx.ifstatement())]
        elif ctx.whilestatement():
            return [self.visit(ctx.whilestatement())]
        elif ctx.forstatement():
            return [self.visit(ctx.forstatement())]
        elif ctx.compoundstatement():
            return self.visit(ctx.compoundstatement())
        elif ctx.withstatement():
            return [self.visit(ctx.withstatement())]
        elif ctx.callstatement():
            return [self.visit(ctx.callstatement())]
        elif ctx.breakstatement():
            return [self.visit(ctx.breakstatement())]
        elif ctx.continuestatement():
            return [self.visit(ctx.continuestatement())]
        else:
            return [self.visit(ctx.returnstatement())]
    def visitAssignmentstatement(self, ctx:MPParser.AssignmentstatementContext):
        A=[]
        len_=len(ctx.assignmentfactor())
        if len_>=2:
            for i in range(len(ctx.assignmentfactor())-1):
                A.append(Assign(self.visit(ctx.assignmentfactor(i)),
                    self.visit(ctx.assignmentfactor(i+1))))
            A.append(Assign(self.visit(ctx.assignmentfactor(len_-1)),self.visit(ctx.expr())))
            A.reverse()
        else:
            A.append(Assign(self.visit(ctx.assignmentfactor(0)),self.visit(ctx.expr())))
        return A
    def visitAssignmentfactor(self, ctx:MPParser.AssignmentfactorContext):
        if ctx.ID():
            return Id(ctx.ID().getText())
        else:
            return self.visit(ctx.indexexpr())
    def visitCallstatement(self, ctx:MPParser.CallstatementContext):
        return CallStmt(Id(ctx.ID().getText()),self.visit(ctx.listexpr()))
    def visitIfstatement(self, ctx:MPParser.IfstatementContext):
        if not ctx.ELSE():
            return If(self.visit(ctx.expr()),self.visit(ctx.statement(0)))
        else:
            return If(self.visit(ctx.expr()),self.visit(ctx.statement(0)),
                self.visit(ctx.statement(1)))
    def visitWhilestatement(self, ctx:MPParser.WhilestatementContext):
        return While(self.visit(ctx.expr()),self.visit(ctx.statement()))
    def visitForstatement(self, ctx:MPParser.ForstatementContext):
        up=None
        if ctx.TO():
            up=True
        else:
            up=False
        return For(Id(ctx.ID().getText()),
                   self.visit(ctx.expr(0)),
                   self.visit(ctx.expr(1)),
                   up,
                   self.visit(ctx.statement()))
    def visitWithstatement(self, ctx:MPParser.WithstatementContext):
        return With(self.visit(ctx.listofvardec()),self.visit(ctx.statement()))
    def visitBreakstatement(self, ctx:MPParser.BreakstatementContext):
        return Break()
    def visitContinuestatement(self, ctx:MPParser.ContinuestatementContext):
        return Continue()
    def visitReturnstatement(self, ctx:MPParser.ReturnstatementContext):
        if not ctx.expr():
            return Return()
        else:
            return Return(self.visit(ctx.expr()))
    def visitListexpr(self, ctx:MPParser.ListexprContext):
        return [self.visit(i) for i in ctx.expr()] if ctx.expr() else []
    def visitExpr(self, ctx:MPParser.ExprContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr1())
        if ctx.AND() and ctx.THEN():
            return BinaryOp("andthen",self.visit(ctx.expr()),self.visit(ctx.expr1()))
        elif ctx.OR() and ctx.ELSE():
            return BinaryOp("orelse",self.visit(ctx.expr()),self.visit(ctx.expr1()))
    def visitExpr1(self, ctx:MPParser.Expr1Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr2()[0])
        left,right=[self.visit(i) for i in ctx.expr2()]
        if ctx.EQ():
            return BinaryOp(ctx.EQ().getText(),left,right)
        elif ctx.NE():
            return BinaryOp(ctx.NE().getText(),left,right)
        elif ctx.LT():
            return BinaryOp(ctx.LT().getText(),left,right)
        elif ctx.LTE():
            return BinaryOp(ctx.LTE().getText(),left,right)
        elif ctx.GT():
            return BinaryOp(ctx.GT().getText(),left,right)
        else:
            return BinaryOp(ctx.GTE().getText(),left,right)
    def visitExpr2(self, ctx:MPParser.Expr2Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr3())
        if ctx.SUB():
            return BinaryOp(ctx.SUB().getText(),self.visit(ctx.expr2()),self.visit(ctx.expr3()))
        if ctx.ADD():
            return BinaryOp(ctx.ADD().getText(),self.visit(ctx.expr2()),self.visit(ctx.expr3()))
        else:
            return BinaryOp(ctx.OR().getText(),self.visit(ctx.expr2()),self.visit(ctx.expr3()))
    def visitExpr3(self, ctx:MPParser.Expr3Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr4())
        if ctx.MUL(): 
            return BinaryOp(ctx.MUL().getText(),self.visit(ctx.expr3()),self.visit(ctx.expr4()))
        elif ctx.INTEGERDIV(): 
            return BinaryOp(ctx.INTEGERDIV().getText(),self.visit(ctx.expr3()),self.visit(ctx.expr4()))
        elif ctx.MOD(): 
            return BinaryOp(ctx.MOD().getText(),self.visit(ctx.expr3()),self.visit(ctx.expr4()))
        elif ctx.AND(): 
            return BinaryOp(ctx.AND().getText(),self.visit(ctx.expr3()),self.visit(ctx.expr4()))
        else:
            return BinaryOp(ctx.DIV().getText(),self.visit(ctx.expr3()),self.visit(ctx.expr4()))
    def visitExpr4(self, ctx:MPParser.Expr4Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr5())
        if ctx.NOT():
            return UnaryOp(ctx.NOT().getText(),self.visit(ctx.expr4()))
        else:
            return UnaryOp(ctx.SUB().getText(),self.visit(ctx.expr4()))
    def visitExpr5(self, ctx:MPParser.Expr5Context):
        if ctx.expr():
            return self.visit(ctx.expr())
        else:
            return self.visit(ctx.factor())
    def visitFactor(self, ctx:MPParser.FactorContext):
        if ctx.invocationexpr():
            return self.visit(ctx.invocationexpr())
        elif ctx.indexexpr():
            return self.visit(ctx.indexexpr())
        elif ctx.BOOLLIT():
            if ctx.BOOLLIT().getText().lower()=="true":
                return BooleanLiteral(True)
            else:
                return BooleanLiteral(False)
        elif ctx.STRINGLIT():
            return StringLiteral(ctx.STRINGLIT().getText())
        elif ctx.INTLIT():
            return IntLiteral(int(ctx.INTLIT().getText()))
        elif ctx.REALLIT():
            return FloatLiteral(float(ctx.REALLIT().getText()))
        else :
            return Id(ctx.ID().getText())
    def visitInvocationexpr(self, ctx:MPParser.InvocationexprContext): 
        return CallExpr(Id(ctx.ID().getText()),self.visit(ctx.listexpr()))
    def visitIndexexpr(self, ctx:MPParser.IndexexprContext):
        return ArrayCell(self.visit(ctx.factor1()),self.visit(ctx.expr()))
    def visitFactor1(self, ctx:MPParser.Factor1Context):  
        if ctx.expr():
            return self.visit(ctx.expr())
        elif ctx.invocationexpr():
            return self.visit(ctx.invocationexpr())
        elif ctx.BOOLLIT():
            if ctx.BOOLLIT().getText().lower()=="true":
                return BooleanLiteral(True)
            else:
                return BooleanLiteral(False)
        elif ctx.STRINGLIT():
            return StringLiteral(ctx.STRINGLIT().getText())
        elif ctx.INTLIT():
            return IntLiteral(int(ctx.INTLIT().getText()))
        elif ctx.REALLIT():
            return FloatLiteral(float(ctx.REALLIT().getText()))
        else:
            return Id(ctx.ID().getText())     
    def visitListofvardec(self, ctx:MPParser.ListofvardecContext):
        return[VarDecl(x,self.visit(ctx.mtype()[i])) 
            for i in range(int(ctx.getChildCount()/4)) 
            for x in self.visit(ctx.listid()[i])]
    def visitListid(self, ctx:MPParser.ListidContext):
        return [Id(i.getText()) for i in ctx.ID()]
    def visitPardec(self, ctx:MPParser.PardecContext):
        len_=len(ctx.listid())
        return[VarDecl(x,self.visit(ctx.mtype(i)))
            for i in range(len_)
            for x in self.visit(ctx.listid(i))]
    def visitMtype(self,ctx:MPParser.MtypeContext):
        if ctx.BOOLEAN():
            return BoolType()
        elif ctx.INTEGER():
            return IntType()
        elif ctx.REAL():
            return FloatType()
        elif ctx.STRING():
            return StringType()
        elif ctx.arraydec():
            return self.visit(ctx.arraydec())
        else:
            return VoidType()
    def visitArraydec(self,ctx:MPParser.ArraydecContext):
        type_=None
        if ctx.BOOLEAN():
            type_= BoolType()
        elif ctx.INTEGER():
            type_= IntType()
        elif ctx.REAL():
            type_= FloatType()
        elif ctx.STRING():
            type_= StringType()
        else:
            type_= VoidType()
        lower,upper=self.visit(ctx.range_())
        return ArrayType(lower,upper,type_)
    def visitRange_(self,ctx:MPParser.Range_Context):
        return [self.visit(i) for i in ctx.limitingint()]
    def visitLimitingint(self,ctx:MPParser.LimitingintContext):
        if ctx.SUB():
            return int(ctx.SUB().getText()+ctx.INTLIT().getText())
        else:
            return int(ctx.INTLIT().getText())