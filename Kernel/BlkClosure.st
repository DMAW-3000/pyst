"======================================================================
|
|   BlockClosure Method Definitions
|
|
 ======================================================================"

"======================================================================
|
| Copyright 1999, 2000, 2001, 2002, 2003, 2007, 2008, 2009
| Free Software Foundation, Inc.
| Written by Steve Byrne.
|
| This file is part of the GNU Smalltalk class library.
|
| The GNU Smalltalk class library is free software; you can redistribute it
| and/or modify it under the terms of the GNU Lesser General Public License
| as published by the Free Software Foundation; either version 2.1, or (at
| your option) any later version.
| 
| The GNU Smalltalk class library is distributed in the hope that it will be
| useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
| General Public License for more details.
| 
| You should have received a copy of the GNU Lesser General Public License
| along with the GNU Smalltalk class library; see the file COPYING.LIB.
| If not, write to the Free Software Foundation, 59 Temple Place - Suite
| 330, Boston, MA 02110-1301, USA.  
|
 ======================================================================"


Object subclass: BlockClosure [
    | outerContext block receiver |
    
    <category: 'Language-Implementation'>
    <comment: 'I am a factotum class.  My instances represent Smalltalk blocks, portions
of executeable code that have access to the environment that they were
declared in, take parameters, and can be passed around as objects to be
executed by methods outside the current class.
Block closures are sent a message to compute their value and create a new
execution context; this property can be used in the construction of
control flow methods.  They also provide some methods that are used in the
creation of Processes from blocks.'>

    BlockClosure class >> numArgs: args numTemps: temps bytecodes: bytecodes depth: depth literals: literalArray [
	"Answer a BlockClosure for a new CompiledBlock that is created using
	 the passed parameters.  To make it work, you must put the BlockClosure
	 into a CompiledMethod's literals."

	<category: 'instance creation'>
	^self block: (CompiledBlock 
		    numArgs: args
		    numTemps: temps
		    bytecodes: bytecodes
		    depth: depth
		    literals: literalArray)
    ]

    BlockClosure class >> isImmediate [
	"Answer whether, if x is an instance of the receiver, x copy == x"

	<category: 'testing'>
	^true
    ]

    copy [
	<category: 'overriding'>
	^self	"We only have one instance"
    ]

    deepCopy [
	"Answer a shallow copy."
	<category: 'overriding'>
	^self shallowCopy	"it's about as deep as we need to get"
    ]

    ensure: aBlock [
	"Evaluate the receiver; when any exception is signaled exit returning the
	 result of evaluating aBlock; if no exception is raised, return the result
	 of evaluating aBlock when the receiver has ended"

	<category: 'unwind protection'>
	| result |
	result := self valueAndResumeOnUnwind.
	aBlock value.
	^result
    ]

    valueWithUnwind [
	"Evaluate the receiver. Any errors caused by the block will cause a
	 backtrace, but execution will continue in the method that sent
	 #valueWithUnwind, after that call. Example:
	 [ 1 / 0 ] valueWithUnwind.
	 'unwind works!' printNl.
	 
	 Important: this method is public, but it is intended to be used in
	 very special cases (as a rule of thumb, use it only when the
	 corresponding C code uses the _gst_prepare_execution_environment and
	 _gst_finish_execution_environment functions). You should usually
	 rely on #ensure: and #on:do:."

	<category: 'unwind protection'>
	thisContext mark.
	^self value
    ]

    repeat [
	"Evaluate the receiver 'forever' (actually until a return is executed
	 or the process is terminated)."

	"When the receiver is a block expression, repeat is optimized
	 by the compiler"

	<category: 'control structures'>
	self value repeat
    ]

    whileTrue: aBlock [
	"Evaluate the receiver. If it returns true, evaluate aBlock and restart"

	"When the receiver is a block expression, whileTrue: is optimized
	 by the compiler"

	<category: 'control structures'>
	self value ifTrue: [aBlock value.
	                    self whileTrue: aBlock].
	^nil
    ]

    whileFalse: aBlock [
	"Evaluate the receiver. If it returns false, evaluate aBlock and restart"

	"When the receiver is a block expression, whileFalse: is optimized
	 by the compiler"

	<category: 'control structures'>
	self value ifFalse: [aBlock value.
	                     self whileFalse: aBlock].
	^nil
    ]

    whileTrue [
	"Evaluate the receiver until it returns false"

	"When the receiver is a block expression, whileTrue is optimized
	 by the compiler"

	<category: 'control structures'>
	^self value ifTrue: [self whileTrue]
    ]

    whileFalse [
	"Evaluate the receiver until it returns true"

	"When the receiver is a block expression, whileFalse is optimized
	 by the compiler"

	<category: 'control structures'>
	^self value ifFalse: [self whileFalse]
    ]
	
    hasMethodReturn [
	"Answer whether the block contains a method return"

	<category: 'testing'>
	^self method 
	    hasBytecode: 124
	    between: self initialIP
	    and: self finalIP
    ]

    fixTemps [
	"This should fix the values of the temporary variables used in the
	 block that are ordinarily shared with the method in which the block
	 is defined.  Not defined yet, but it is not harmful that it isn't.
	 Answer the receiver."

	<category: 'accessing'>
	^self
    ]

    block [
	"Answer the CompiledBlock which contains the receiver's bytecodes"

	<category: 'accessing'>
	^block
    ]

    block: aCompiledBlock [
	"Set the CompiledBlock which contains the receiver's bytecodes"

	<category: 'accessing'>
	block := aCompiledBlock
    ]

    finalIP [
	"Answer the last instruction that can be executed by the receiver"

	<category: 'accessing'>
	^self block size
    ]

    initialIP [
	"Answer the initial instruction pointer into the receiver."

	<category: 'accessing'>
	^1
    ]

    argumentCount [
	"Answer the number of arguments passed to the receiver"

	<category: 'accessing'>
	^block numArgs
    ]

    numArgs [
	"Answer the number of arguments passed to the receiver"

	<category: 'accessing'>
	^block numArgs
    ]

    numTemps [
	"Answer the number of temporary variables used by the receiver"

	<category: 'accessing'>
	^block numTemps
    ]

    stackDepth [
	"Answer the number of stack slots needed for the receiver"

	<category: 'accessing'>
	^block stackDepth
    ]

    method [
	"Answer the CompiledMethod in which the receiver lies"

	<category: 'accessing'>
	^block method
    ]

    receiver [
	"Answer the object that is used as `self' when executing the receiver
	 (if nil, it might mean that the receiver is not valid though...)"

	<category: 'accessing'>
	^receiver
    ]

    receiver: anObject [
	"Set the object that is used as `self' when executing the receiver"

	<category: 'accessing'>
	receiver := anObject
    ]

    outerContext [
	"Answer the method/block context which is the immediate outer of
	 the receiver"

	<category: 'accessing'>
	^outerContext
    ]

    outerContext: containingContext [
	"Set the method/block context which is the immediate outer of
	 the receiver"

	<category: 'accessing'>
	outerContext := containingContext
    ]

    value [
	"Evaluate the receiver passing no parameters"

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_value>
	"SystemExceptions." WrongArgumentCount signal
    ]

    value: arg1 [
	"Evaluate the receiver passing arg1 as the only parameter"

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_value>
	"SystemExceptions." WrongArgumentCount signal
    ]

    value: arg1 value: arg2 [
	"Evaluate the receiver passing arg1 and arg2 as the parameters"

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_value>
	"SystemExceptions." WrongArgumentCount signal
    ]

    value: arg1 value: arg2 value: arg3 [
	"Evaluate the receiver passing arg1, arg2 and arg3 as the parameters"

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_value>
	"SystemExceptions." WrongArgumentCount signal
    ]

    cull: arg1 [
	"Evaluate the receiver, passing arg1 as the only parameter if
	 the receiver has parameters."

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_cull>
	"SystemExceptions." WrongArgumentCount signal
    ]

    cull: arg1 cull: arg2 [
	"Evaluate the receiver, passing arg1 and arg2 as parameters if
	 the receiver accepts them."

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_cull>
	"SystemExceptions." WrongArgumentCount signal
    ]

    cull: arg1 cull: arg2 cull: arg3 [
	"Evaluate the receiver, passing arg1, arg2 and arg3 as parameters if
	 the receiver accepts them."

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_cull>
	"SystemExceptions." WrongArgumentCount signal
    ]

    valueWithArguments: argumentsArray [
	"Evaluate the receiver passing argArray's elements as the parameters"

	<category: 'built ins'>
	<primitive: VMpr_BlockClosure_valueWithArguments>
	argumentsArray isArray 
	    ifFalse: ["SystemExceptions." WrongClass signalOn: argumentsArray mustBe: Array].
	"SystemExceptions." WrongArgumentCount signal
    ]

    method: aCompiledCode [
        <category: 'private'>

        block method: aCompiledCode
    ]

    valueAndResumeOnUnwind [
	"Private - For use by #ensure:"

	<category: 'private'>
	<primitive: VMpr_BlockClosure_valueAndResumeOnUnwind>
	"SystemExceptions."WrongArgumentCount signal
    ]
]

