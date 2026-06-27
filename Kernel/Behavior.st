"======================================================================
|
|   Behavior Method Definitions
|
|
 ======================================================================"

"======================================================================
|
| Copyright 1988,89,90,91,92,94,95,99,2000,2001,2002,2003,
| 2005,2006,2007,2008,2009 Free Software Foundation, Inc.
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

Object subclass: Behavior [
    | superClass methodDictionary instanceSpec subClasses instanceVariables |
    
    <category: 'Language-Implementation'>
    <comment: 'I am the parent class of all "class" type methods.  My instances know
about the subclass/superclass relationships between classes, contain
the description that instances are created from, and hold the method
dictionary thats associated with each class.  I provide methods for
compiling methods, modifying the class inheritance hierarchy, examining the
method dictionary, and iterating over the class hierarchy.'>


    new [
        "Create a new instance of a class with no indexed instance variables"
        <primitive: VMpr_Behavior_newInitialize>
        <category: 'builtin'>
        self isFixed ifFalse: [ ^(self new: 0) ].
        ^self primitiveFailed
    ]
	
	new: numInstanceVariables [
        "Create a new instance of a class with indexed instance variables. The
        instance has numInstanceVariables indexed instance variables."
        <primitive: VMpr_Behavior_newColonInitialize>
        <category: 'builtin'>
        self isFixed ifTrue: [
            "SystemExceptions." WrongMessageSent signalOn: #new: useInstead: #new
        ].
        numInstanceVariables isSmallInteger ifTrue: [ ^self primitiveFailed ].

        ^"SystemExceptions." WrongClass signalOn: numInstanceVariables mustBe: SmallInteger
    ]

    basicNew [
        "Create a new instance of a class with no indexed instance variables;
         this method must not be overridden."
        <primitive: VMpr_Behavior_basicNew>
        <category: 'builtin'>
        self isFixed ifFalse: [ ^self basicNew: 0 ].
        ^self primitiveFailed
    ]
    
    basicNew: numInstanceVariables [
        "Create a new instance of a class with indexed instance variables. The
         instance has numInstanceVariables indexed instance variables;
         this method must not be overridden."
        <primitive: VMpr_Behavior_basicNewColon>
        <category: 'builtin'>
        self isFixed ifTrue: [
    	"SystemExceptions." WrongMessageSent signalOn: #basicNew: useInstead: #basicNew
        ].
        numInstanceVariables isSmallInteger ifTrue: [ ^self primitiveFailed ].
    
        ^"SystemExceptions." WrongClass signalOn: numInstanceVariables mustBe: SmallInteger
    ]
	
	methodDictionary [
	"Answer the receiver's method dictionary. Don't modify the method
	 dictionary unless you exactly know what you're doing"

	<category: 'method dictionary'>
	^methodDictionary
    ]

    selectorsAndMethodsDo: aBlock [
	"Evaluate aBlock, passing for each evaluation a selector that's
	 defined in the receiver and the corresponding method."

	<category: 'method dictionary'>
	self methodDictionary isNil 
	    ifFalse: [self methodDictionary keysAndValuesDo: aBlock]
    ]
	
	superclass: aClass [
	"Set the receiver's superclass."

	<category: 'creating a class hierarchy'>
	superClass := aClass.
	instanceSpec isNil 
	    ifTrue: 
		[instanceSpec := aClass isNil ifTrue: [0] ifFalse: [aClass instanceSpec]]
    ]

    addSubclass: aClass [
	"Add aClass asone of the receiver's subclasses."

	<category: 'creating a class hierarchy'>
	subClasses isNil 
	    ifTrue: [subClasses := Array new]
	    ifFalse: 
		["remove old class if any"

		subClasses := subClasses copyWithout: aClass].
	subClasses := subClasses copyWith: aClass
    ]

    removeSubclass: aClass [
	"Remove aClass from the list of the receiver's subclasses"

	<category: 'creating a class hierarchy'>
	subClasses := subClasses copyWithout: aClass
    ]

    selectors [
	"Answer a Set of the receiver's selectors"

	<category: 'accessing the method dictionary'>
	self methodDictionary isNil 
	    ifTrue: [^Set new]
	    ifFalse: [^self methodDictionary keys]
    ]
	
	lookupSelector: aSelector [
	"Return the compiled method associated with selector, from the local
	 method dictionary or one of a superclass; return nil if not found."

	<category: 'accessing the method dictionary'>
	| class method |
	class := self.
	
	[method := class compiledMethodAt: aSelector ifAbsent: [nil].
	method isNil ifFalse: [^method].
	class := class superclass.
	class isNil ifTrue: [^nil]] 
		repeat
    ]
	
	compiledMethodAt: selector ifAbsent: aBlock [
	"Return the compiled method associated with selector, from the local
	 method dictionary.  Evaluate aBlock if not found."

	<category: 'accessing the method dictionary'>
	self methodDictionary isNil ifTrue: [^aBlock value].
	^self methodDictionary at: selector ifAbsent: aBlock
    ]

    compiledMethodAt: selector [
	"Return the compiled method associated with selector, from the local
	 method dictionary.  Error if not found."

	<category: 'accessing the method dictionary'>
	self methodDictionary isNil 
	    ifTrue: [SystemExceptions.NotFound signalOn: selector what: 'key'].
	^self methodDictionary at: selector
	    ifAbsent: [SystemExceptions.NotFound signalOn: selector what: 'key']
    ]

    >> selector [
	"Return the compiled method associated with selector, from the local
	 method dictionary.  Error if not found."

	<category: 'accessing the method dictionary'>
	self methodDictionary isNil 
	    ifTrue: ["SystemExceptions." NotFound signalOn: selector what: 'key'].
	^self methodDictionary at: selector
	    ifAbsent: ["SystemExceptions." NotFound signalOn: selector what: 'key']
    ]

    selectorAt: method [
	"Return selector for the given CompiledMethod"

	<category: 'accessing the method dictionary'>
	self methodDictionary isNil 
	    ifTrue: ["SystemExceptions. " NotFound signalOn: method what: 'method'].
	^self methodDictionary keyAtValue: method
	    ifAbsent: ["SystemExceptions." NotFound signalOn: method what: 'method']
    ]

	parseTreeFor: selector [
	"Answer the parse tree for the given selector, or nil if there was an
	 error.  Requires the Parser package to be loaded."

	<category: 'accessing the method dictionary'>
	^(self >> selector) methodParseNode
    ]

    sourceCodeAt: selector ifAbsent: aBlock [
	"Answer source code (if available) for the given selector."

	<category: 'accessing the method dictionary'>
	| source |
	source := (self >> selector) methodSourceCode.
	source isNil ifTrue: [^aBlock value copy].
	^source asString
    ]
	
	sourceCodeAt: selector [
	"Answer source code (if available) for the given selector."

	<category: 'accessing the method dictionary'>
	^self sourceCodeAt: selector ifAbsent: [
	    ' *** SOURCE CODE NOT AVAILABLE *** ']
    ]

    sourceMethodAt: selector [
	"This is too dependent on the original implementation"

	<category: 'accessing the method dictionary'>
	self shouldNotImplement
    ]
	
	instanceCount [
	"Return a count of all the instances of the receiver"

	<category: 'accessing instances and variables'>
	| count anInstance |
	count := 0.
	anInstance := self someInstance.
	[anInstance notNil] whileTrue: 
		[count := count + 1.
		anInstance := anInstance nextInstance].
	^count
    ]

    indexOfInstVar: aString [
	"Answer the index of aString in the fixed instance variables of the
	 instances of the receiver, or 0 if the variable is missing."

	<category: 'accessing instances and variables'>
	^self allInstVarNames indexOfLast: aString asSymbol ifAbsent: [0]
    ]

    indexOfInstVar: aString ifAbsent: aBlock [
	"Answer the index of aString in the fixed instance variables of the
	 instances of the receiver, or 0 if the variable is missing."

	<category: 'accessing instances and variables'>
	^self allInstVarNames indexOfLast: aString asSymbol ifAbsent: aBlock
    ]
	
	subclasses [
	"Answer the direct subclasses of the receiver in a Set"

	<category: 'accessing class hierarchy'>
	subClasses isNil ifTrue: [^Set new] ifFalse: [^subClasses asSet]
    ]
	
	withAllSubclasses [
	"Answer a Set containing the receiver together with its direct and
	 indirect subclasses"

	<category: 'accessing class hierarchy'>
	| aSet |
	aSet := Set with: self.
	aSet addAll: self allSubclasses.
	^aSet
    ]

    superclass [
	"Answer the receiver's superclass (if any, otherwise answer nil)"

	<category: 'accessing class hierarchy'>
	^superClass
    ]

	hasMethods [
	"Return whether the receiver has any methods defined"

	<category: 'testing the method dictionary'>
	^self methodDictionary notNil and: [self methodDictionary notEmpty]
    ]

    includesSelector: selector [
	"Returns true if the local method dictionary contains the given selector"

	<category: 'testing the method dictionary'>
	self methodDictionary isNil ifTrue: [^false].
	^self methodDictionary includesKey: selector
    ]

    canUnderstand: selector [
	"Returns true if the instances of the receiver understand
	 the given selector"

	<category: 'testing the method dictionary'>
	^(self lookupSelector: selector) notNil
    ]
	
	isBits [
	"Answer whether my instances' variables are immediate, non-OOP
	 values."
	<category: 'testing the form of the instances'>
	^self shape notNil and: [self isPointers not]
    ]

    isPointers [
	"Answer whether the instance variables of the receiver's instances
	 are objects"

	<category: 'testing the form of the instances'>
	^(self instanceSpec bitAnd: 31) = 31
    ]

    isIdentity [
	"Answer whether x = y implies x == y for instances of the receiver"

	<category: 'testing the form of the instances'>
	^false
    ]

    isImmediate [
	"Answer whether, if x is an instance of the receiver, x copy == x"

	<category: 'testing the form of the instances'>
	^false
    ]

    isFixed [
	"Answer whether the receiver's instances have no indexed
	 instance variables"

	<category: 'testing the form of the instances'>
	^self isVariable not
    ]

    isVariable [
	"Answer whether the receiver's instances have indexed instance variables"

	<category: 'testing the form of the instances'>
	^(self instanceSpec bitAt: 5) ~= 0
    ]

    instSize [
	"Answer how many fixed instance variables are reserved to each of the
	 receiver's instances"

	<category: 'testing the form of the instances'>
	^self instanceSpec bitShift: -12
    ]

    includesBehavior: aClass [
	"Returns true if aClass is the receiver or a superclass of the receiver."

	<category: 'testing the class hierarchy'>
	^self == aClass or: [self inheritsFrom: aClass]
    ]

    inheritsFrom: aClass [
	"Returns true if aClass is a superclass of the receiver"

	<category: 'testing the class hierarchy'>
	| sc |
	aClass isNil ifTrue: [^true].

	sc := self.
	[sc := sc superclass.
	sc isNil] whileFalse: [sc == aClass ifTrue: [^true]].
	^false
    ]

    kindOfSubclass [
	"Return a string indicating the type of class the receiver is"

	<category: 'testing the class hierarchy'>
	self isVariable ifFalse: [^'subclass:'].
	self isPointers ifTrue: [^'variableSubclass:'].
	^'variable: ' , self shape storeString , 'subclass:'
    ]
	
	shape [
	"Answer the symbolic shape of my instances."
	<category: 'testing the class hierarchy'>
	self isVariable ifFalse: [^nil].
	^self shapes at: (instanceSpec bitAnd: 15) + 1
    ]

    allSuperclassesDo: aBlock [
	"Invokes aBlock for all superclasses, both direct and indirect."

	<category: 'enumerating'>
	| class superclass |
	class := self.
	
	[superclass := class superclass.
	class := superclass.
	superclass notNil] 
		whileTrue: [aBlock value: superclass]
    ]

    withAllSubclassesDo: aBlock [
	"Invokes aBlock for the receiver and all subclasses, both direct
	 and indirect."

	<category: 'enumerating'>
	aBlock value: self.
	self allSubclassesDo: aBlock
    ]

    withAllSuperclassesDo: aBlock [
	"Invokes aBlock for the receiver and all superclasses, both direct
	 and indirect."

	<category: 'enumerating'>
	| class |
	class := self.
	
	[aBlock value: class.
	class := class superclass.
	class notNil] whileTrue
    ]

    allInstancesDo: aBlock [
	"Invokes aBlock for all instances of the receiver"

	<category: 'enumerating'>
	| anInstance |
	anInstance := self someInstance.
	[anInstance notNil] whileTrue: 
		[aBlock value: anInstance.
		anInstance := anInstance nextInstance]
    ]

    subclassesDo: aBlock [
	"Invokes aBlock for all direct subclasses."

	<category: 'enumerating'>
	subClasses isNil ifTrue: [^self].
	subClasses do: aBlock
    ]

    methods [
	"Don't use this, it's only present to file in from Smalltalk/V"

	<category: 'compilation (alternative)'>
	^self methodsFor: 'no category'
    ]

    methodsFor [
	"Don't use this, it's only present to file in from Dolphin Smalltalk"

	<category: 'compilation (alternative)'>
	^self methodsFor: 'no category'
    ]

    methodsFor: category ifFeatures: features [
	"Start compiling methods in the receiver if this implementation of
	 Smalltalk has the given features, else skip the section"

	<category: 'compilation (alternative)'>
	^self methodsFor: category ifTrue: (Smalltalk hasFeatures: features)
    ]

    methodsFor: category stamp: notUsed [
	"Don't use this, it's only present to file in from Squeak"

	<category: 'compilation (alternative)'>
	^self methodsFor: category
    ]

    privateMethods [
	"Don't use this, it's only present to file in from IBM Smalltalk"

	<category: 'compilation (alternative)'>
	^self methodsFor: 'private'
    ]

    publicMethods [
	"Don't use this, it's only present to file in from IBM Smalltalk"

	<category: 'compilation (alternative)'>
	^self methodsFor: 'public'
    ]

    article [
	"Answer an article (`a' or `an') which is ok for the receiver's name"

	<category: 'support for lightweight classes'>
	^self superclass article
    ]

    asClass [
	"Answer the first superclass that is a full-fledged Class object"

	<category: 'support for lightweight classes'>
	^self superclass asClass
    ]

    environment [
	"Answer the namespace that this class belongs to - the same as the
	 superclass, since Behavior does not support namespaces yet."

	<category: 'support for lightweight classes'>
	^self superclass environment
    ]

    nameIn: aNamespace [
	"Answer the class name when the class is referenced from aNamespace
	 - a dummy one, since Behavior does not support names."

	<category: 'support for lightweight classes'>
	^'<no name>'
    ]

    printOn: aStream in: aNamespace [
	"Answer the class name when the class is referenced from aNamespace
	 - a dummy one, since Behavior does not support names."

	<category: 'support for lightweight classes'>
	aStream nextPutAll: (self nameIn: aNamespace)
    ]

    newInFixedSpace: numInstanceVariables [
	"Create a new instance of a class with indexed instance variables. The
	 instance has numInstanceVariables indexed instance variables.  The
	 instance is guaranteed not to move across garbage collections.  If
	 a subclass overrides #new:, the changes will apply to this method too."

	<category: 'instance creation'>
	^(self new: numInstanceVariables) makeFixed
    ]

    newInFixedSpace [
	"Create a new instance of a class without indexed instance variables.
	 The instance is guaranteed not to move across garbage collections.
	 If a subclass overrides #new, the changes will apply to this method too."

	<category: 'instance creation'>
	^self new makeFixed
    ]

	instanceSpec [
	<category: 'private'>
	^instanceSpec
    ]
	
	sharedPoolDictionaries [
	"Return the shared pools (not the names!) defined by the class"

	<category: 'private'>
	^self superclass sharedPoolDictionaries
    ]

    setInstanceVariables: instVariableArray [
	<category: 'private'>
	instanceVariables := instVariableArray
    ]
	
	updateInstanceVars: variableArray shape: shape [
	"Update instance variables and instance spec of the class and all
	 its subclasses.  variableArray lists the new variables, including
	 inherited ones."
	^self
	    updateInstanceVars: variableArray
	    superclass: self superclass
	    shape: shape
    ]
	
	isBehavior [
	<category: 'testing functionality'>
	^true
    ]

    debuggerClass [
	"Answer which class is to be used to debug a chain of contexts which
	 includes the receiver.  nil means 'do not debug'; other classes are
	 sent #debuggingPriority and the one with the highest priority is
	 picked."

	<category: 'pluggable behavior (not yet implemented)'>
	^nil
    ]

    decompilerClass [
	"Answer the class that can be used to decompile methods,
	 or nil if there is none (as is the case now)."

	<category: 'pluggable behavior (not yet implemented)'>
	^nil
    ]

    evaluatorClass [
	"Answer the class that can be used to evaluate doits,
	 or nil if there is none (as is the case now)."

	<category: 'pluggable behavior (not yet implemented)'>
	^nil
    ]

    parserClass [
	"Answer the class that can be used to parse methods,
	 or nil if there is none (as is the case now)."

	<category: 'pluggable behavior (not yet implemented)'>
	^nil
    ]

    compilerClass [
	"Answer the class that can be used to compile parse trees,
	 or nil if there is none (as is the case now).  Not
	 used for methods if parserClass answers nil, and for
	 doits if evaluatorClass answers nil."

	<category: 'pluggable behavior (not yet implemented)'>
	^nil
    ]

    printHierarchy [
	"Print my entire subclass hierarchy on the terminal."

	<category: 'printing hierarchy'>
	self printSubclasses: 0
    ]

   	hierarchyIndent [
	"Answer the indent to be used by #printHierarchy - 4 by default"

	<category: 'printing hierarchy'>
	^4
    ]

    flushCache [
	"Invalidate the method cache kept by the virtual machine. This
	 message should not need to be called by user programs."

	<category: 'built ins'>
	<primitive: VMpr_Behavior_flushCache>
	^self primitiveFailed
    ]

    basicNewInFixedSpace: numInstanceVariables [
	"Create a new instance of a class with indexed instance variables. The
	 instance has numInstanceVariables indexed instance variables.  The
	 instance is guaranteed not to move across garbage collections.  Like
	 #basicNew:, this method should not be overridden."

	<category: 'built ins'>
	<primitive: VMpr_Behavior_basicNewFixedColon>
	self isFixed 
	    ifTrue: 
		["SystemExceptions." WrongMessageSent signalOn: #basicNewInFixedSpace:
		    useInstead: #basicNewInFixedSpace].
	numInstanceVariables isSmallInteger ifTrue: [^self primitiveFailed].
	^"SystemExceptions." WrongClass signalOn: numInstanceVariables
	    mustBe: SmallInteger
    ]

    basicNewInFixedSpace [
	"Create a new instance of a class with no indexed instance variables.
	 The instance is guaranteed not to move across garbage collections.
	 Like #basicNew, this method should not be overridden."

	<category: 'built ins'>
	<primitive: VMpr_Behavior_basicNewFixed>
	self isFixed ifTrue: [^self primitiveFailed].
	"SystemExceptions." WrongMessageSent signalOn: #basicNewInFixedSpace
	    useInstead: #basicNewInFixedSpace:
    ]

    someInstance [
	"Private - Answer the first instance of the receiver in the object
	 table"

	<category: 'built ins'>
	<primitive: VMpr_Behavior_someInstance>
	^nil	"return nil on failure"
    ]

    methodsFor: category ifTrue: condition [
	"Compile the following code inside the receiver, with the given
	 category, if condition is true; else ignore it"

	<category: 'built ins'>
	<primitive: VMpr_Behavior_methodsForIfTrue>
	^self primitiveFailed
    ]

    primCompile: code [
	"Compile the code, a string or readable stream, with no
	 category. Fail if the code does not obey Smalltalk syntax. Answer
	 the generated CompiledMethod if it does.
	 
	 Do not send this in user code; use #compile: or related methods
	 instead."

	<category: 'built ins'>
	<primitive: VMpr_Behavior_primCompile>
	^self primitiveFailed
    ]

    primCompile: code ifError: aBlock [
	"As with #primCompile:, but evaluate aBlock (passing the file
	 name, line number and description of the error) if the code does
	 not obey Smalltalk syntax.
	 
	 Do not send this in user code; use #compile:ifError: or related
	 methods instead."

	<category: 'built ins'>
	<primitive: VMpr_Behavior_primCompileIfError>
	^self primitiveFailed
    ]

    scopeDictionary [
        "Answer the dictionary that is used when the receiver is before
         a period in Smalltalk source code."
        <category: 'compilation'>
        ^self classPool
    ]
]
      