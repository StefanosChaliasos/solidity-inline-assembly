"""
Taxonomy of inline assembly OPCODES and instructions.
"""
ARITHMETIC_OPERATIONS = {
    'Arithmetic Operations': [
        'add',
        'sub',
        'mul',
        'div',
        'sdiv',
        'mod',
        'smod',
        'addmod',
        'mulmod',
        'exp',
        'signextend'
    ]
}

COMPARISON_BITWISE = {
    'Comparison': [
        'lt',
        'gt',
        'slt',
        'sgt',
        'eq',
    ],
    'Bitwise Logic': [
        'iszero',
        'and',
        'or',
        'xor',
        'not',
        'byte',
        'shl',
        'shr',
        'sar'
    ]
}

HASH_OPERATIONS = {
    'KECCAK256': [
        'keccak256',
        'sha3'
    ]
}

ENVIROMENTAL_INFORMATION = {
    'Current Environment': [
        'address',
        'origin',
        'caller',
        'callvalue',
        'calldataload',
        'calldatasize',
        'calldatacopy',
        'codesize',
        'codecopy',
        'gasprice',
        'returndatasize',
        'returndatacopy',
        'selfbalance',
        'chainid',
        'gas'
    ],
    'Account Information': [
        'balance',
        'extcodesize',
        'extcodecopy',
        'extcodehash'
    ],
}

BLOCK_INFORMATION = {
    'Block Information': [
        'blockhash',
        'coinbase',
        'timestamp',
        'number',
        'difficulty',
        'gaslimit'
    ]
}

STACK_MEMORY_STORAGE = {
    'Stack': [
        'pop',
        'pc'
    ],
    'Memory': [
        'mload',
        'mstore',
        'mstore8',
        'msize'
    ], 
    'Storage': [
        'sload',
        'sstore'
    ]
}

FLOW_OPERATIONS = {
    'YUL Control Flow': [
        'for',
        'if',
        'switch',
        'leave'
    ],
    'Control Flow Opcodes': [
        'jump',
        'jumpi',
        'jumpdest'
    ]
}

PUSH_DUP_SWAP = {
    'Push, Duplication, and Exchange': [
        'push',
        'dup',
        'swap'
    ]
}

LOGGING_OPERATIONS = {
    'Logging Operations': [
        'log0',
        'log1',
        'log2',
        'log3',
        'log4'
    ]
}
YUL_DECLARATIONS = {
    'YUL Declarations': [
        'let',
        'function'
    ]
}

YUL_SPECIAL_INSTRUCTIONS = {
    'YUL Special Instructions': [
        'datasize',
        'dataoffset',
        'datacopy',
        'setimmutable',
        'loadimmutable',
        'linkersymbol',
        'memoryguard',
        'verbatim'
    ]
}

SYSTEM_OPERATIONS = {
    'Call': [
        'call',
        'callcode',
        'delegatecall',
        'staticcall'
    ],
    'Create': [
        'create',
        'create2'
    ],
    'Execution': [
        'return',
        'revert',
        'selfdestruct',
        'stop'
    ],
    'Invalid': [
        'invalid'
    ]
}
