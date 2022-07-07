"""
Implement a visitor for SolidityVisitor from
https://github.com/ConsenSys/python-solidity-parser
to process inline assembly in a Solidity file.
"""
import argparse
import os
import json
import statistics
import itertools

from collections import defaultdict

from library.assembly_types import OPCODES, OLD_OPCODES, \
    HIGH_LEVEL_CONSTRUCTS, DECLARATIONS, SPECIAL

from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4 import FileStream, CommonTokenStream
from solidity_parser.solidity_antlr4.SolidityLexer import SolidityLexer
from solidity_parser.solidity_antlr4.SolidityParser import SolidityParser
from solidity_parser.solidity_antlr4.SolidityVisitor import SolidityVisitor


def _get_loc(ctx):
        return {
            'start': {
                'line': ctx.start.line,
                'column': ctx.start.column
            },
            'end': {
                'line': ctx.stop.line,
                'column': ctx.stop.column
            }
        }


def _get_text(ctx):
    token_source = ctx.start.getTokenSource()
    input_stream = token_source.inputStream
    return input_stream.getText(ctx.start.start, ctx.stop.stop)


def _compute_lines(loc):
    return loc['end']['line'] - loc['start']['line'] + 1


class Node(dict):
    """
    provide a dict interface and object attrib access
    """
    def __init__(self, ctx, **kwargs):
        for k, v in kwargs.items():
            self[k] = v
        self["text"] = Node._get_text(ctx)

    def __getattr__(self, item):
        return self[item]  # raise exception if attribute does not exist

    def __setattr__(self, name, value):
        self[name] = value

    @staticmethod
    def _get_text(ctx):
        return _get_text(ctx)


class Contract:
    def __init__(self, name):
        self.name = name
        self.code = None
        self.lines = None
        self.fragments = []
        self.computed_total_lines = 0
        self.functions = 0  # funcs + modifiers
        self.functions_with_inline_assembly = 0

    def get_name(self):
        return self.name

    def get_fragments(self):
        return self.fragments

    def get_total_fragments(self):
        return len(self.fragments)

    def get_total_lines(self):
        return _compute_lines(self.lines)

    def get_total_assembly_lines(self):
        return sum(_compute_lines(f['loc']) for f in self.fragments)

    def get_total_functions(self):
        return self.functions

    def get_total_functions_with_inline_assembly(self):
        return self.functions_with_inline_assembly

    def get_total_inline_functions(self):
        return sum(len(f['functions']) for f in self.fragments)

    def get_total_definitions(self):
        return sum(len(f['definitions']) for f in self.fragments)

    def get_declarations(self):
        res = [('let', self.get_total_definitions()),
               ('function', self.get_total_inline_functions())]
        return {decl: value for decl, value in res if value > 0}

    def get_total_label_definitions(self):
        return sum(len(f['label_definitions']) for f in self.fragments)

    def get_total_assignments(self):
        return sum(len(f['assignments']) for f in self.fragments)

    def get_total_if(self):
        return sum(len(f['if_stmts']) for f in self.fragments)

    def get_total_for(self):
        return sum(len(f['for_stmts']) for f in self.fragments)

    def get_total_switch(self):
        return sum(len(f['switch_stmts']) for f in self.fragments)

    def get_opcodes(self):
        results = defaultdict(lambda: 0)
        for f in self.fragments:
            for opcode, value in f['calls_counter']['OPCODES'].items():
                results[opcode] += value
        return results

    def get_old_opcodes(self):
        results = defaultdict(lambda: 0)
        for f in self.fragments:
            for opcode, value in f['calls_counter']['OLD_OPCODES'].items():
                results[opcode] += value
        return results

    def get_special_opcodes(self):
        results = defaultdict(lambda: 0)
        for f in self.fragments:
            for opcode, value in f['calls_counter']['SPECIAL'].items():
                results[opcode] += value
        return results

    def get_high_level_constructs(self):
        res = [(construct, getattr(Contract, 'get_total_' + construct)(self))
               for construct in ['if', 'switch', 'for']]
        return {contstruct: value for contstruct, value in res if value > 0}

    def has_assembly(self):
        return self.get_total_fragments() > 0

    def to_json_results(self, include_code=False):
        res = {
            'stats': {
                'lines': self.get_total_lines(),
                'funcs': self.get_total_functions(),
                'funcs with assembly': self.get_total_functions_with_inline_assembly(),
                'assembly fragments': self.get_total_fragments(),
                'assembly lines': self.get_total_assembly_lines(),
                'has_assembly': self.get_total_fragments() > 0,
                'opcodes': self.get_opcodes(),
                'old opcodes': self.get_old_opcodes(),
                'special opcodes': self.get_special_opcodes(),
                'high-level constructs': self.get_high_level_constructs(),
                'declarations': self.get_declarations()
            },
            'fragments': [f.to_json_results(include_code)
                          for f in self.fragments]
        }
        if include_code:
            res['code'] = self.code
        return res


class InlineAssemblyFragment(dict):

    def __init__(self, ctx, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

        self['loc'] = InlineAssemblyFragment._get_loc(ctx)
        self['code'] = InlineAssemblyFragment._get_text(ctx)

        self['assignments'] = []
        self['functions'] = []
        self['definitions'] = []
        self['label_definitions'] = []
        self['if_stmts'] = []
        self['switch_stmts'] = []
        self['for_stmts'] = []
        # instructions
        self['calls'] = []

        self['calls_counter'] = defaultdict(lambda: defaultdict(lambda: 0))

    def __getattr__(self, item):
        return self[item]  # raise exception if attribute does not exist

    def __setattr__(self, name, value):
        if name == 'calls_counter':
            if value in OPCODES:
                self[name]['OPCODES'][value] += 1
            elif value in OLD_OPCODES:
                self[name]['OLD_OPCODES'][value] += 1
            elif value in SPECIAL:
                self[name]['SPECIAL'][value] += 1
        elif isinstance(self[name], list):
            self[name].append(value)
        else:
            self[name] = value

    @staticmethod
    def _get_loc(ctx):
        return _get_loc(ctx)

    @staticmethod
    def _get_text(ctx):
        return _get_text(ctx)

    def get_total_lines(self):
        return _compute_lines(self['loc'])

    def get_opcodes(self):
        return self['calls_counter']['OPCODES']

    def get_old_opcodes(self):
        return self['calls_counter']['OLD_OPCODES']

    def get_special_opcodes(self):
        return self['calls_counter']['SPECIAL']

    def get_high_level_constructs(self):
        res = [(construct, len(self[construct + '_stmts']))
               for construct in ['if', 'switch', 'for']]
        return {contstruct: value for contstruct, value in res if value > 0}

    def get_declarations(self):
        res = [('let', len(self['definitions'])),
               ('function', len(self['functions']))]
        return {decl: value for decl, value in res if value > 0}

    def to_json_results(self, include_code=False):
        res = {
            'original_lines': self['loc'],
            'lines': self.get_total_lines(),
            'opcodes': self.get_opcodes(),
            'old opcodes': self.get_old_opcodes(),
            'special opcodes': self.get_special_opcodes(),
            'high-level constructs': self.get_high_level_constructs(),
            'declarations': self.get_declarations()
        }
        # Always include
        res['code'] = self.code
        return res


class FileInlineAssemblyData:

    def __init__(self, name):
        self.name = name
        self.code = None
        self.solidity_version = None
        self.contracts = []
        # this class may contain the contracts of multiple files
        self.total_lines = []

    def get_contracts(self):
        return self.contracts

    def to_json_results(self, include_code=False):
        res = {}
        res['contracts'] = {c.get_name(): c.to_json_results()
                            for c in self.contracts}
        res['lines'] = self.get_total_lines()
        res['solidity_version'] = self.solidity_version
        if include_code:
            res['code'] = self.code
        return res

    ##### Helper functions to process results #####

    def get_total_contracts(self):
        return len(self.contracts)

    def get_total_functions(self):
        return sum(c.get_total_functions() for c in self.contracts)

    def get_total_lines(self):
        return sum(_compute_lines(l) for l in self.total_lines)

    def get_total_contracts_with_inline_assembly(self):
        return sum(1 for c in self.contracts if c.get_total_fragments() > 0)

    def get_total_functions_with_inline_assembly(self):
        return sum(c.get_total_functions_with_inline_assembly()
                   for c in self.contracts)

    def get_total_assembly_lines(self):
        return sum(c.get_total_assembly_lines() for c in self.contracts)

    def get_total_fragments(self):
        return sum(c.get_total_fragments() for c in self.contracts)

    def get_opcodes(self):
        res = defaultdict(lambda: 0)
        for c in self.contracts:
            for opcode, value in c.get_opcodes().items():
                res[opcode] += value
        return res

    def get_old_opcodes(self):
        res = defaultdict(lambda: 0)
        for c in self.contracts:
            for opcode, value in c.get_old_opcodes().items():
                res[opcode] += value
        return res

    def get_special_opcodes(self):
        res = defaultdict(lambda: 0)
        for c in self.contracts:
            for opcode, value in c.get_special_opcodes().items():
                res[opcode] += value
        return res

    def get_high_level_constructs(self):
        res = defaultdict(lambda: 0)
        for c in self.contracts:
            for contstruct, value in c.get_high_level_constructs().items():
                res[contstruct] += value
        return res

    def get_declarations(self):
        res = defaultdict(lambda: 0)
        for c in self.contracts:
            for decl, value in c.get_declarations().items():
                res[decl] += value
        return res

    def get_total_definitions(self):
        return sum(c.get_total_definitions() for c in self.contracts)


class InlineAssemblyData:

    def __init__(self, files):
        assert isinstance(files, list)
        self.files = files

    def compute(self, name, result_type):
        method = getattr(FileInlineAssemblyData, name)
        if result_type == 'sum':
            return sum(method(f) for f in self.files)
        elif result_type == 'dict':
            res = defaultdict(lambda: 0)
            for f in self.files:
                for k, value in method(f).items():
                    res[k] += value
            return res
        else:
            raise Exception("result_type should be sum or dict")

    def to_json_results(self, include_code=False):
        return {f.name: f.to_json_results(include_code) for f in self.files}


class InlineAssemblyVisitor(SolidityVisitor):

    def __init__(self, name=''):
        super(InlineAssemblyVisitor, self).__init__()
        self.data = FileInlineAssemblyData(name)
        self.contracts = self.data.contracts

        self._current_fragment = None

        self._current_contract = None

        self._current_func_mod_has_assembly = None

    # start helper functions

    def _mapCommasToNulls(self, children):
        if not children or len(children) == 0:
            return []

        values = []
        comma = True

        for el in children:
            if comma:
                if el.getText() == ',':
                    values.append(None)
                else:
                    values.append(el)
                    comma = False
            else:
                if el.getText() != ',':
                    raise Exception('expected comma')

                comma = True

        if comma:
            values.append(None)

        return values

    def _createNode(self, **kwargs):
        ## todo: add loc!
        return Node(**kwargs)

    def visit(self, tree):
        """
        override the default visit to optionally accept a range of children nodes

        :param tree:
        :return:
        """
        if tree is None:
            return None
        elif isinstance(tree, list):
            return self._visit_nodes(tree)
        else:
            return super().visit(tree)

    def _visit_nodes(self, nodes):
        """
        modified version of visitChildren() that returns an array of results

        :param nodes:
        :return:
        """
        allresults = []
        result = self.defaultResult()
        for c in nodes:
            childResult = c.accept(self)
            result = self.aggregateResult(result, childResult)
            allresults.append(result)
        return allresults

    # end helper functions

    def visitSourceUnit(self, ctx):
        self.data.code = _get_text(ctx)
        loc = _get_loc(ctx)
        self.data.total_lines.append(loc)
        return self.visitChildren(ctx)

    def visitPragmaDirective(self, ctx):
        pragma_name = ctx.pragmaName().getText()
        pragma_value = ctx.pragmaValue().getText()
        if pragma_name == 'solidity':
            self.data.solidity_version = pragma_value
        return Node(ctx=ctx,
                    type="PragmaDirective",
                    name=pragma_name,
                    value=pragma_value)

    def visitImportDirective(self, ctx):
        symbol_aliases = {}
        unit_alias = None

        if len(ctx.importDeclaration()) > 0:
            for item in ctx.importDeclaration():

                try:
                    alias = item.identifier(1).getText()
                except:
                    alias = None
                symbol_aliases[item.identifier(0).getText()] = alias

        elif len(ctx.children) == 7:
            unit_alias = ctx.getChild(3).getText()

        elif len(ctx.children) == 5:
            unit_alias = ctx.getChild(3).getText()

        return Node(ctx=ctx,
                    type="ImportDirective",
                    path=ctx.importPath().getText().strip('"'),
                    symbolAliases=symbol_aliases,
                    unitAlias=unit_alias
                    )

    def visitContractDefinition(self, ctx):
        old_contract = self._current_contract

        contract_name = ctx.identifier().getText()
        self._current_contract = Contract(contract_name)
        self._current_contract.lines = _get_loc(ctx)
        self._current_contract.code = _get_text(ctx)
        self.data.contracts.append(self._current_contract)

        node = Node(ctx=ctx,
                    type="ContractDefinition",
                    name=ctx.identifier().getText(),
                    baseContracts=self.visit(ctx.inheritanceSpecifier()),
                    subNodes=self.visit(ctx.contractPart()),
                    kind=ctx.getChild(0).getText())

        self._current_contract = old_contract

        return node

    def visitModifierDefinition(self, ctx):
        old = self._current_func_mod_has_assembly
        self._current_func_mod_has_assembly = False

        parameters = []

        if ctx.parameterList():
            parameters = self.visit(ctx.parameterList())

        node = Node(ctx=ctx,
                    type='ModifierDefinition',
                    name=ctx.identifier().getText(),
                    parameters=parameters,
                    body=self.visit(ctx.block()))

        self._current_contract.functions += 1
        if self._current_func_mod_has_assembly:
            self._current_contract.functions_with_inline_assembly += 1
        self._current_func_mod_has_assembly = old
        return node

    def visitFunctionDefinition(self, ctx):
        old = self._current_func_mod_has_assembly
        self._current_func_mod_has_assembly = False

        isConstructor = isFallback = isReceive = False

        # In some cases, although we have parsed all children of a contract
        # in visitContractDefinition, some functions that are defined in the
        # last contract may be parsed outside of visitContractDefinition.
        # That is why we manually set self._current_contract
        use_previous_contract = False
        old_contract = self._current_contract
        if self._current_contract is None:
            # FIXME
            # Still this may fail, check
            #data/complete_dataset/assembly/0x804ce08ccdf0d22fb4d1d8e12d9f4ea51e9cd804.sol
            #data/complete_dataset/assembly/0x804cd786a44ba0b21fab162d981be390315777eb.sol
            #data/complete_dataset/assembly/0x804cddbdb345f741544be554be9a9b27327bbdf8.sol
            #data/complete_dataset/assembly/0x804cd929b1ebb749862a32b6fd0959ef637af31c.sol
            #data/complete_dataset/assembly/0x804cd95d24dbe0b3877975d60997a7a5eeb658e8.sol
            #data/complete_dataset/assembly/0x804cdb9116a10bb78768d3252355a1b18067bf8f.sol

            self._current_contract = self.contracts[-1]


        fd = ctx.functionDescriptor()
        if fd.ConstructorKeyword():
            name = fd.ConstructorKeyword().getText()
            isConstructor = True
        elif fd.FallbackKeyword():
            name = fd.FallbackKeyword().getText()
            isFallback = True
        elif fd.ReceiveKeyword():
            name = fd.ReceiveKeyword().getText()
            isReceive = True
        elif fd.identifier():
            name = fd.identifier().getText()
        else:
            name = ctx.getText()

        parameters = self.visit(ctx.parameterList())
        returnParameters = self.visit(ctx.returnParameters()) if ctx.returnParameters() else []
        block = self.visit(ctx.block()) if ctx.block() else []
        modifiers = [self.visit(i) for i in ctx.modifierList().modifierInvocation()]

        if ctx.modifierList().ExternalKeyword(0):
            visibility = "external"
        elif ctx.modifierList().InternalKeyword(0):
            visibility = "internal"
        elif ctx.modifierList().PublicKeyword(0):
            visibility = "public"
        elif ctx.modifierList().PrivateKeyword(0):
            visibility = "private"
        else:
            visibility = 'default'

        if ctx.modifierList().stateMutability(0):
            stateMutability = ctx.modifierList().stateMutability(0).getText()
        else:
            stateMutability = None

        node = Node(ctx=ctx,
                    type="FunctionDefinition",
                    name=name,
                    parameters=parameters,
                    returnParameters=returnParameters,
                    body=block,
                    visibility=visibility,
                    modifiers=modifiers,
                    isConstructor=isConstructor,
                    isFallback=isFallback,
                    isReceive=isReceive,
                    stateMutability=stateMutability)

        self._current_contract.functions += 1
        if self._current_func_mod_has_assembly:
            self._current_contract.functions_with_inline_assembly += 1
        self._current_func_mod_has_assembly = old
        self._current_contract = old_contract
        return node

    # start inline assembly

    def visitInlineAssemblyStatement(self, ctx):
        assert self._current_fragment is None

        fragment = InlineAssemblyFragment(ctx)
        self._current_fragment = fragment
        self._current_contract.fragments.append(fragment)

        language = None

        if ctx.StringLiteralFragment():
            language = ctx.StringLiteralFragment().getText()
            language = language[1: len(language) - 1]

        if self._current_func_mod_has_assembly is not None:
            self._current_func_mod_has_assembly = True

        body = self.visit(ctx.assemblyBlock())

        self._current_fragment = None
        fragment['body'] = body


        node = Node(ctx=ctx,
                    type='InLineAssemblyStatement',
                    language=language,
                    body=body)

        return node

    def visitAssemblyBlock(self, ctx):
        assert self._current_fragment is not None

        operations = [self.visit(it) for it in ctx.assemblyItem()]

        node = Node(ctx,
                    type="AssemblyBlock",
                    operations=operations)

        return node

    def visitAssemblyItem(self, ctx):
        assert self._current_fragment is not None

        name = None
        txt = None

        if ctx.hexLiteral():
            txt = ctx.hexLiteral().getText()
            name = 'HexLiteral'
        elif ctx.stringLiteral():
            txt = ctx.stringLiteral().getText()
            txt = txt[1: len(txt) - 1]
            name = 'StringLiteral'
        elif ctx.BreakKeyword():
            name = 'Break'
        elif ctx.ContinueKeyword():
            name = 'Continue'

        if name:
            node = Node(ctx=ctx,
                        type=name)
            if txt:
                node['value'] = txt

        return self.visit(ctx.getChild(0))

    def visitAssemblyExpression(self, ctx):
        assert self._current_fragment is not None
        return self.visit(ctx.getChild(0))

    def visitAssemblyMember(self, ctx):
        assert self._current_fragment is not None
        try:
            name = ctx.identifier().getText()
        except:
            try:
                name = ctx.identifier()[0].getText()
            except:
                name = ''
        return Node(ctx=ctx,
                    type='AssemblyMember',
                    name=name)

    def visitAssemblyCall(self, ctx):
        assert self._current_fragment is not None
        functionName = ctx.getChild(0).getText()
        args = [self.visit(arg) for arg in ctx.assemblyExpression()]
        args = [arg for arg in args if arg is not None]

        node = Node(ctx=ctx,
                    type='AssemblyExpression',
                    functionName=functionName,
                    arguments=args)

        self._current_fragment.calls_counter = functionName
        self._current_fragment.calls = node

        return node

    def visitAssemblyLiteral(self, ctx):
        assert self._current_fragment is not None
        name = None

        if ctx.stringLiteral():
            text = ctx.getText()
            text = text[1: len(text) - 1]
            name = 'StringLiteral'

        if ctx.DecimalNumber():
            text = ctx.getText()
            name = 'DecimalNumber'

        if ctx.HexNumber():
            text = ctx.getText()
            name = 'HexNumber'

        if ctx.hexLiteral():
            text = ctx.getText()
            name = 'HexLiteral'

        if name:
            return Node(ctx=ctx,
                        type=name,
                        value=text)

    def visitAssemblySwitch(self, ctx):
        assert self._current_fragment is not None
        node = Node(ctx=ctx,
                    type='AssemblySwitch',
                    expression=self.visit(ctx.assemblyExpression()),
                    cases=[self.visit(c) for c in ctx.assemblyCase()])
        self._current_fragment.switch_stmts = node
        return node

    def visitAssemblyCase(self, ctx):
        assert self._current_fragment is not None
        value = None

        if ctx.getChild(0).getText() == 'case':
            value = self.visit(ctx.assemblyLiteral())

        block = self.visit(ctx.assemblyBlock())
        if value is None:
            value = True

        return Node(ctx=ctx,
                    type="AssemblyCase",
                    block=block,
                    value=value)

    def visitAssemblyLocalDefinition(self, ctx):
        assert self._current_fragment is not None
        names = ctx.assemblyIdentifierOrList()

        if names.identifier():
            names = [self.visit(names.identifier())]
        else:
            names = self.visit(names.assemblyIdentifierList().identifier())

        expression = self.visit(ctx.assemblyExpression())

        node = Node(ctx=ctx,
                    type='AssemblyLocalDefinition',
                    names=names,
                    expression=expression)
        self._current_fragment.definitions = node

        return node

    def visitAssemblyFunctionDefinition(self, ctx):
        assert self._current_fragment is not None
        try:
            args = ctx.assemblyIdentifierList().identifier()
        except:
            args = None
        try:
            returnArgs = ctx.assemblyFunctionReturns().assemblyIdentifierList().identifier()
        except:
            returnArgs = None
        body = self.visit(ctx.assemblyBlock())
        name = ctx.identifier().getText()
        node = Node(ctx=ctx,
                    type='AssemblyFunctionDefinition',
                    name=name,
                    arguments=self.visit(args),
                    returnArguments=self.visit(returnArgs),
                    body=body)
        self._current_fragment.functions = node
        return node

    def visitAssemblyAssignment(self, ctx):
        assert self._current_fragment is not None
        names = ctx.assemblyIdentifierOrList()

        if names.identifier():
            names = [self.visit(names.identifier())]
        else:
            try:
                names = self.visit(names.assemblyIdentifierList().identifier())
            except:
                names = []

        expression = self.visit(ctx.assemblyExpression())

        node = Node(ctx=ctx,
                    type='AssemblyAssignment',
                    names=names,
                    expression=expression)

        self._current_fragment.assignments = node

        return node

    def visitLabelDefinition(self, ctx):
        assert self._current_fragment is not None

        node = Node(ctx=ctx,
                    type='LabelDefinition',
                    name=ctx.identifier().getText())

        self._current_fragment.label_definitions = node

        return node

    def visitAssemblyStackAssignment(self, ctx):
        assert self._current_fragment is not None
        return Node(ctx=ctx,
                    type='AssemblyStackAssignment',
                    name=ctx.identifier().getText())

    def visitAssemblyFor(self, ctx):
        assert self._current_fragment is not None
        node = Node(ctx=ctx,
                    type='AssemblyFor',
                    pre=self.visit(ctx.getChild(1)),
                    condition=self.visit(ctx.getChild(2)),
                    post=self.visit(ctx.getChild(3)),
                    body=self.visit(ctx.getChild(4)))
        self._current_fragment.for_stmts = node
        return node

    def visitAssemblyIf(self, ctx):
        assert self._current_fragment is not None
        node = Node(ctx=ctx,
                    type='AssemblyIf',
                    condition=self.visit(ctx.assemblyExpression()),
                    body=self.visit(ctx.assemblyBlock()))
        self._current_fragment.if_stmts = node
        return node

    # end inline assembly

    def visitEnumDefinition(self, ctx):
        return Node(ctx=ctx,
                    type="EnumDefinition",
                    name=ctx.identifier().getText(),
                    members=self.visit(ctx.enumValue()))

    def visitEnumValue(self, ctx):
        return Node(ctx=ctx,
                    type="EnumValue",
                    name=ctx.identifier().getText())

    def visitTypeDefinition(self, ctx):
        return Node(ctx=ctx,
                    type="TypeDefinition",
                    typeKeyword=ctx.TypeKeyword().getText(),
                    elementaryTypeName=self.visit(ctx.elementaryTypeName()))


    def visitCustomErrorDefinition(self, ctx):
        return Node(ctx=ctx,
                    type="CustomErrorDefinition",
                    name=self.visit(ctx.identifier()),
                    parameterList=self.visit(ctx.parameterList()))

    def visitFileLevelConstant(self, ctx):
        return Node(ctx=ctx,
                    type="FileLevelConstant",
                    name=self.visit(ctx.identifier()),
                    typeName=self.visit(ctx.typeName()),
                    ConstantKeyword=self.visit(ctx.ConstantKeyword()))

    def visitUsingForDeclaration(self, ctx: SolidityParser.UsingForDeclarationContext):
        typename = None
        if ctx.getChild(3) != '*':
            typename = self.visit(ctx.getChild(3))

        return Node(ctx=ctx,
                    type="UsingForDeclaration",
                    typeName=typename,
                    libraryName=ctx.identifier().getText())

    def visitInheritanceSpecifier(self, ctx: SolidityParser.InheritanceSpecifierContext):
        return Node(ctx=ctx,
                    type="InheritanceSpecifier",
                    baseName=self.visit(ctx.userDefinedTypeName()),
                    arguments=self.visit(ctx.expressionList()))

    def visitContractPart(self, ctx: SolidityParser.ContractPartContext):
        if ctx.children is None:
            return self.visit(None)
        return self.visit(ctx.children[0])

    def visitReturnParameters(self, ctx: SolidityParser.ReturnParametersContext):
        return self.visit(ctx.parameterList())

    def visitParameterList(self, ctx: SolidityParser.ParameterListContext):
        parameters = [self.visit(p) for p in ctx.parameter()]
        return Node(ctx=ctx,
                    type="ParameterList",
                    parameters=parameters)

    def visitParameter(self, ctx: SolidityParser.ParameterContext):

        storageLocation = ctx.storageLocation().getText() if ctx.storageLocation() else None
        name = ctx.identifier().getText() if ctx.identifier() else None

        return Node(ctx=ctx,
                    type="Parameter",
                    typeName=self.visit(ctx.typeName()),
                    name=name,
                    storageLocation=storageLocation,
                    isStateVar=False,
                    isIndexed=False
                    )

    def visitModifierInvocation(self, ctx):
        exprList = ctx.expressionList()

        if exprList is not None:
            args = self.visit(exprList.expression())
        else:
            args = []

        return Node(ctx=ctx,
                    type='ModifierInvocation',
                    name=ctx.identifier().getText(),
                    arguments=args)

    def visitElementaryTypeNameExpression(self, ctx):
        return Node(ctx=ctx,
                    type='ElementaryTypeNameExpression',
                    typeName=self.visit(ctx.elementaryTypeName()))

    def visitTypeName(self, ctx):
        if len(ctx.children) > 2:
            length = None
            if len(ctx.children) == 4:
                length = self.visit(ctx.getChild(2))

            return Node(ctx=ctx,
                        type='ArrayTypeName',
                        baseTypeName=self.visit(ctx.getChild(0)),
                        length=length)

        if len(ctx.children) == 2:
            return Node(ctx=ctx,
                        type='ElementaryTypeName',
                        name=ctx.getChild(0).getText(),
                        stateMutability=ctx.getChild(1).getText())

        return self.visit(ctx.getChild(0))

    def visitFunctionTypeName(self, ctx):
        parameterTypes = [self.visit(p) for p in ctx.functionTypeParameterList(0).functionTypeParameter()]
        returnTypes = []

        if ctx.functionTypeParameterList(1):
            returnTypes = [self.visit(p) for p in ctx.functionTypeParameterList(1).functionTypeParameter()]

        visibility = 'default'
        if ctx.InternalKeyword(0):
            visibility = 'internal'
        elif ctx.ExternalKeyword(0):
            visibility = 'external'

        stateMutability = None
        if ctx.stateMutability(0):
            stateMutability = ctx.stateMutability(0).getText()

        return Node(ctx=ctx,
                    type='FunctionTypeName',
                    parameterTypes=parameterTypes,
                    returnTypes=returnTypes,
                    visibility=visibility,
                    stateMutability=stateMutability)

    def visitFunctionCall(self, ctx):
        args = []
        names = []

        ctxArgs = ctx.functionCallArguments()

        if ctxArgs.expressionList():
            args = [self.visit(a) for a in ctxArgs.expressionList().expression()]

        elif ctxArgs.nameValueList():
            for nameValue in ctxArgs.nameValueList().nameValue():
                args.append(self.visit(nameValue.expression()))
                names.append(nameValue.identifier().getText())

        return Node(ctx=ctx,
                    type='FunctionCall',
                    expression=self.visit(ctx.expression()),
                    arguments=args,
                    names=names)

    def visitEmitStatement(self, ctx):
        return Node(ctx=ctx,
                    type='EmitStatement',
                    eventCall=self.visit(ctx.getChild(1)))

    def visitThrowStatement(self, ctx):
        return Node(ctx=ctx,
                    type='ThrowStatement')

    def visitStructDefinition(self, ctx):
        return Node(ctx=ctx,
                    type='StructDefinition',
                    name=ctx.identifier().getText(),
                    members=self.visit(ctx.variableDeclaration()))

    def visitVariableDeclaration(self, ctx):
        storageLocation = None

        if ctx.storageLocation():
            storageLocation = ctx.storageLocation().getText()

        return Node(ctx=ctx,
                    type='VariableDeclaration',
                    typeName=self.visit(ctx.typeName()),
                    name=ctx.identifier().getText(),
                    storageLocation=storageLocation)

    def visitEventParameter(self, ctx):
        storageLocation = None

        # TODO: fixme

        # if (ctx.storageLocation(0)):
        #    storageLocation = ctx.storageLocation(0).getText()

        return Node(ctx=ctx,
                    type='VariableDeclaration',
                    typeName=self.visit(ctx.typeName()),
                    name=ctx.identifier().getText(),
                    storageLocation=storageLocation,
                    isStateVar=False,
                    isIndexed=not not ctx.IndexedKeyword())

    def visitFunctionTypeParameter(self, ctx):
        storageLocation = None

        if ctx.storageLocation():
            storageLocation = ctx.storageLocation().getText()

        return Node(ctx=ctx,
                    type='VariableDeclaration',
                    typeName=self.visit(ctx.typeName()),
                    name=None,
                    storageLocation=storageLocation,
                    isStateVar=False,
                    isIndexed=False)

    def visitWhileStatement(self, ctx):
        return Node(ctx=ctx,
                    type='WhileStatement',
                    condition=self.visit(ctx.expression()),
                    body=self.visit(ctx.statement()))

    def visitDoWhileStatement(self, ctx):
        return Node(ctx=ctx,
                    type='DoWhileStatement',
                    condition=self.visit(ctx.expression()),
                    body=self.visit(ctx.statement()))

    def visitIfStatement(self, ctx):

        try:
            TrueBody = self.visit(ctx.statement(0))
        except:
            # There is a parsing error inside the true body
            # (probably a missing ';')
            TrueBody = None

        FalseBody = None
        if len(ctx.statement()) > 1:
            FalseBody = self.visit(ctx.statement(1))

        return Node(ctx=ctx,
                    type='IfStatement',
                    condition=self.visit(ctx.expression()),
                    TrueBody=TrueBody,
                    FalseBody=FalseBody)

    def visitTryStatement(self, ctx):
        return Node(ctx=ctx,
                    type='TryStatement',
                    expression=self.visit(ctx.expression()),
                    block=self.visit(ctx.block()),
                    returnParameters=self.visit(ctx.returnParameters()),
                    catchClause=self.visit(ctx.catchClause()))

    def visitCatchClause(self, ctx):
        return Node(ctx=ctx,
                    type='CatchClause',
                    identifier=self.visit(ctx.identifier()),
                    parameterList=self.visit(ctx.parameterList()),
                    block=self.visit(ctx.block()))

    def visitUserDefinedTypeName(self, ctx):
        return Node(ctx=ctx,
                    type='UserDefinedTypeName',
                    namePath=ctx.getText())

    def visitElementaryTypeName(self, ctx):
        return Node(ctx=ctx,
                    type='ElementaryTypeName',
                    name=ctx.getText())

    def visitBlock(self, ctx):
        return Node(ctx=ctx,
                    type='Block',
                    statements=self.visit(ctx.statement()))

    def visitExpressionStatement(self, ctx):
        return Node(ctx=ctx,
                    type='ExpressionStatement',
                    expression=self.visit(ctx.expression()))

    def visitNumberLiteral(self, ctx):
        number = ctx.getChild(0).getText()
        subdenomination = None

        if len(ctx.children) == 2:
            subdenomination = ctx.getChild(1).getText()

        return Node(ctx=ctx,
                    type='NumberLiteral',
                    number=number,
                    subdenomination=subdenomination)

    def visitMapping(self, ctx):
        return Node(ctx=ctx,
                    type='Mapping',
                    keyType=self.visit(ctx.mappingKey()),
                    valueType=self.visit(ctx.typeName()))

    def visitStatement(self, ctx):
        return self.visit(ctx.getChild(0))

    def visitSimpleStatement(self, ctx):
        try:
            return self.visit(ctx.getChild(0))
        except:
            # There is a but in antlr4/ParserRuleContext.py instead of
            # raising an exception it should return None
            return None

    def visitUncheckedStatement(self, ctx):
        return Node(ctx=ctx,
                    type='UncheckedStatement',
                    body=self.visit(ctx.block()))

    def visitRevertStatement(self, ctx):
        return Node(ctx=ctx,
                    type='RevertStatement',
                    functionCall=self.visit(ctx.functionCall()))

    def visitExpression(self, ctx):

        children_length = len(ctx.children) if ctx.children is not None else 0
        if children_length == 1:
            return self.visit(ctx.getChild(0))

        elif children_length == 2:
            op = ctx.getChild(0).getText()
            if op == 'new':
                return Node(ctx=ctx,
                            type='NewExpression',
                            typeName=self.visit(ctx.typeName()))

            if op in ['+', '-', '++', '--', '!', '~', 'after', 'delete']:
                return Node(ctx=ctx,
                            type='UnaryOperation',
                            operator=op,
                            subExpression=self.visit(ctx.getChild(1)),
                            isPrefix=True)

            op = ctx.getChild(1).getText()
            if op in ['++', '--']:
                return Node(ctx=ctx,
                            type='UnaryOperation',
                            operator=op,
                            subExpression=self.visit(ctx.getChild(0)),
                            isPrefix=False)
        elif children_length == 3:
            if ctx.getChild(0).getText() == '(' and ctx.getChild(2).getText() == ')':
                return Node(ctx=ctx,
                            type='TupleExpression',
                            components=[self.visit(ctx.getChild(1))],
                            isArray=False)

            op = ctx.getChild(1).getText()

            if op == ',':
                return Node(ctx=ctx,
                            type='TupleExpression',
                            components=[
                                self.visit(ctx.getChild(0)),
                                self.visit(ctx.getChild(2))
                            ],
                            isArray=False)


            elif op == '.':
                expression = self.visit(ctx.getChild(0))
                memberName = ctx.getChild(2).getText()
                return Node(ctx=ctx,
                            type='MemberAccess',
                            expression=expression,
                            memberName=memberName)

            binOps = [
                '+',
                '-',
                '*',
                '/',
                '**',
                '%',
                '<<',
                '>>',
                '&&',
                '||',
                '&',
                '|',
                '^',
                '<',
                '>',
                '<=',
                '>=',
                '==',
                '!=',
                '=',
                '|=',
                '^=',
                '&=',
                '<<=',
                '>>=',
                '+=',
                '-=',
                '*=',
                '/=',
                '%='
            ]

            if op in binOps:
                return Node(ctx=ctx,
                            type='BinaryOperation',
                            operator=op,
                            left=self.visit(ctx.getChild(0)),
                            right=self.visit(ctx.getChild(2)))

        elif children_length == 4:

            if ctx.getChild(1).getText() == '(' and ctx.getChild(3).getText() == ')':
                args = []
                names = []

                ctxArgs = ctx.functionCallArguments()
                if ctxArgs.expressionList():
                    args = [self.visit(a) for a in ctxArgs.expressionList().expression()]
                elif ctxArgs.nameValueList():
                    for nameValue in ctxArgs.nameValueList().nameValue():
                        args.append(self.visit(nameValue.expression()))
                        names.append(nameValue.identifier().getText())

                return Node(ctx=ctx,
                            type='FunctionCall',
                            expression=self.visit(ctx.getChild(0)),
                            arguments=args,
                            names=names)

            if ctx.getChild(1).getText() == '[' and ctx.getChild(3).getText() == ']':
                return Node(ctx=ctx,
                            type='IndexAccess',
                            base=self.visit(ctx.getChild(0)),
                            index=self.visit(ctx.getChild(2)))

        elif children_length == 5:
            # ternary
            if ctx.getChild(1).getText() == '?' and ctx.getChild(3).getText() == ':':
                return Node(ctx=ctx,
                            type='Conditional',
                            condition=self.visit(ctx.getChild(0)),
                            TrueExpression=self.visit(ctx.getChild(2)),
                            FalseExpression=self.visit(ctx.getChild(4)))

        return self.visit(list(ctx.getChildren()))


    def visitStateVariableDeclaration(self, ctx):
        type = self.visit(ctx.typeName())
        iden = ctx.identifier()
        # FIXME
        #data/complete_dataset/assembly/0x7e571b13AeB1A6ABcFC470B7d033a6838e53f440.sol
        #data/complete_dataset/assembly/0x7e5603e7f842f3eae62bce12f9cfb2139f8259d4.sol
        #data/complete_dataset/assembly/0x7e5720b925659f711f8c243f21e3856d2f0dcc71.sol
        #data/complete_dataset/assembly/0x7e562c205a1F696ba155Caf3d179cd4a5C41EF21.sol
        #data/complete_dataset/assembly/0x7e576556b91ce912c0a2a16f96f4d491230fc3a8.sol
        #data/complete_dataset/assembly/0x7E5782E1B694631bCef49acF2aD600c293c40026.sol
        name = iden.getText()

        expression = None

        if ctx.expression():
            expression = self.visit(ctx.expression())

        visibility = 'default'

        if ctx.InternalKeyword(0):
            visibility = 'internal'
        elif ctx.PublicKeyword(0):
            visibility = 'public'
        elif ctx.PrivateKeyword(0):
            visibility = 'private'

        isDeclaredConst = False
        if ctx.ConstantKeyword(0):
            isDeclaredConst = True

        decl = self._createNode(
            ctx=ctx,
            type='VariableDeclaration',
            typeName=type,
            name=name,
            expression=expression,
            visibility=visibility,
            isStateVar=True,
            isDeclaredConst=isDeclaredConst,
            isIndexed=False)

        return Node(ctx=ctx,
                    type='StateVariableDeclaration',
                    variables=[decl],
                    initialValue=expression)

    def visitForStatement(self, ctx):
        conditionExpression = self.visit(ctx.expressionStatement()) if ctx.expressionStatement() else None

        if conditionExpression:
            conditionExpression = conditionExpression.expression

        return Node(ctx=ctx,
                    type='ForStatement',
                    initExpression=self.visit(ctx.simpleStatement()),
                    conditionExpression=conditionExpression,
                    loopExpression=Node(ctx=ctx,
                        type='ExpressionStatement',
                        expression=self.visit(ctx.expression())),
                    body=self.visit(ctx.statement())
                    )

    def visitPrimaryExpression(self, ctx):
        if ctx.BooleanLiteral():
            return Node(ctx=ctx,
                        type='BooleanLiteral',
                        value=ctx.BooleanLiteral().getText() == 'true')

        if ctx.hexLiteral():
            return Node(ctx=ctx,
                        type='hexLiteral',
                        value=ctx.hexLiteral().getText())

        if ctx.stringLiteral():
            text = ctx.getText()
            return Node(ctx=ctx,
                        type='stringLiteral',
                        value=text[1: len(text) - 1])

        if len(ctx.children) == 3 and ctx.getChild(1).getText() == '[' and ctx.getChild(2).getText() == ']':
            node = self.visit(ctx.getChild(0))
            if node.type == 'Identifier':
                node = Node(ctx=ctx,
                            type='UserDefinedTypeName',
                            namePath=node.name)
            else:
                node = Node(ctx=ctx,
                            type='ElementaryTypeName',
                            name=ctx.getChild(0).getText())

            return Node(ctx=ctx,
                        type='ArrayTypeName',
                        baseTypeName=node,
                        length=None)

        return self.visit(ctx.getChild(0))

    def visitIdentifier(self, ctx):
        return Node(ctx=ctx,
                    type="Identifier",
                    name=ctx.getText())

    def visitTupleExpression(self, ctx):
        children = ctx.children[1:-1]
        components = [None if e is None else self.visit(e) for e in self._mapCommasToNulls(children)]

        return Node(ctx=ctx,
                    type='TupleExpression',
                    components=components,
                    isArray=ctx.getChild(0).getText() == '[')

    def visitIdentifierList(self, ctx: SolidityParser.IdentifierListContext):
        children = ctx.children[1:-1]

        result = []
        for iden in self._mapCommasToNulls(children):
            if iden == None:
                result.append(None)
            else:
                result.append(self._createNode(ctx=ctx,
                                               type="VariableDeclaration",
                                               name=iden.getText(),
                                               isStateVar=False,
                                               isIndexed=False,
                                               iden=iden))

        return result

    def visitVariableDeclarationList(self, ctx: SolidityParser.VariableDeclarationListContext):
        result = []
        for decl in self._mapCommasToNulls(ctx.children):
            if decl == None:
                return None

            result.append(self._createNode(ctx=ctx,
                                           type='VariableDeclaration',
                                           name=decl.identifier().getText(),
                                           typeName=self.visit(decl.typeName()),
                                           isStateVar=False,
                                           isIndexed=False,
                                           decl=decl))

        return result

    def visitVariableDeclarationStatement(self, ctx):

        if ctx.variableDeclaration():
            variables = [self.visit(ctx.variableDeclaration())]
        elif ctx.identifierList():
            variables = self.visit(ctx.identifierList())
        elif ctx.variableDeclarationList():
            variables = self.visit(ctx.variableDeclarationList())

        initialValue = None

        if ctx.expression():
            initialValue = self.visit(ctx.expression())

        return Node(ctx=ctx,
                    type='VariableDeclarationStatement',
                    variables=variables,
                    initialValue=initialValue)

    def visitEventDefinition(self, ctx):
        return Node(ctx=ctx,
                    type='EventDefinition',
                    name=ctx.identifier().getText(),
                    parameters=self.visit(ctx.eventParameterList()),
                    isAnonymous=not not ctx.AnonymousKeyword())

    def visitEventParameterList(self, ctx):
        parameters = []
        for paramCtx in ctx.eventParameter():
            type = self.visit(paramCtx.typeName())
            name = None
            if paramCtx.identifier():
                name = paramCtx.identifier().getText()

            parameters.append(self._createNode(ctx=ctx,
                type='VariableDeclaration',
                typeName=type,
                name=name,
                isStateVar=False,
                isIndexed=not not paramCtx.IndexedKeyword()))

        return Node(ctx=ctx,
                    type='ParameterList',
                    parameters=parameters)

    def visitUserDefinedTypename(self, ctx):
        return Node(ctx=ctx,
                    type="UserDefinedTypename",
                    name=ctx.getText())

    def visitReturnStatement(self, ctx):
        return self.visit(ctx.expression())

    def visitTerminal(self, ctx):
        return ctx.getText()

def parse(filename, text, start="sourceUnit"):
    input_stream = InputStream(text)

    lexer = SolidityLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = SolidityParser(token_stream)
    inline_visitor = InlineAssemblyVisitor(filename)

    inline_visitor.visit(getattr(parser, start)())

    return inline_visitor.data


def parse_file(path, start="sourceUnit"):
    with open(path, 'r', encoding="utf-8") as f:
        return parse(path, f.read(), start=start)


def parse_input(path):
    if os.path.isfile(path):
        return InlineAssemblyData([parse_file(path)])
    elif os.path.isdir(path):
        files = [os.path.join(path, f) for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f)) and '.sol' in f]
        results = [parse_file(f) for f in files]
        return InlineAssemblyData(results)
    else:
        raise FileNotFoundError(f"{path} does not exists")


def get_top(opcodes):
    sorted_opcodes = list(sorted(opcodes.items(),
                                 key=lambda item: item[1],
                                 reverse=True))[:5]
    opcodes = ", ".join(["{} ({})".format(op, count)
                        for op, count in sorted_opcodes])
    return opcodes

def print_statistics(data):
    contracts = data.compute('get_total_contracts', 'sum')
    print(f"Number of contracts: {contracts}")
    functions = data.compute('get_total_functions', 'sum')
    print(f"Number of functions: {functions}")
    lines = data.compute('get_total_lines', 'sum')
    print(f"Number of lines: {lines}")
    print()
    as_contracts = data.compute('get_total_contracts_with_inline_assembly', 'sum')
    print(f"Number of contracts with assembly: {as_contracts}")
    as_functions = data.compute('get_total_functions_with_inline_assembly', 'sum')
    print(f"Number of functions with assembly : {as_functions}")
    as_lines = data.compute('get_total_assembly_lines', 'sum')
    print(f"Number of assembly lines: {as_lines}")
    fragments = data.compute('get_total_fragments', 'sum')
    print(f"Number of assembly fragments: {fragments}")

    print()
    opcodes = get_top(data.compute('get_opcodes', 'dict'))
    if opcodes:
        print(f"Top OPCODES: {opcodes}")
    old_opcodes = get_top(data.compute('get_old_opcodes', 'dict'))
    if old_opcodes:
        print(f"Top OLD OPCODES: {old_opcodes}")
    high_level_constructs = get_top(
        data.compute('get_high_level_constructs', 'dict'))
    if high_level_constructs:
        print(f"Top HIGH_LEVEL_CONSTRUCTS: {high_level_constructs}")
    declarations = get_top(data.compute('get_declarations', 'dict'))
    if declarations:
        print(f"Top DECLARATIONS: {declarations}")


def get_args():
    parser = argparse.ArgumentParser(
        description='Process inline assembly of a solidity file')
    parser.add_argument(
        "file", help="Path of the solidity file or directory with solidity files"
    )
    parser.add_argument(
        "-p", "--print",
        action='store_true',
        help="Print statistics"
    )
    parser.add_argument(
        "-s", "--save",
        help="Save results to JSON"
    )
    parser.add_argument(
        "-c", "--code",
        action="store_true",
        help="Save Code"
    )
    return parser.parse_args()


def main():
    args = get_args()
    print(f"Processing file: {args.file}")
    data = parse_input(args.file)
    if args.print:
        print_statistics(data)
    if args.save:
        with open(args.save, 'w') as f:
            json.dump(data.to_json_results(args.code), f)


if __name__ == "__main__":
    main()
