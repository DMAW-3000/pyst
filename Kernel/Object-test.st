"======================================================================
|
|   Object Method Definitions
|
|
 ======================================================================"

"======================================================================
|
| Copyright 1990,1991,1992,94,95,99,2000,2001,2002,2003,2007,2008,2009
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

nil subclass: Object [
    
    <comment: 'I am the root of the Smalltalk class system. 
All classes in the system are subclasses of me.'>
    <category: 'Language-Implementation'>

    Dependencies := nil.
    FinalizableObjects := nil.
    FinalSemaphore := nil.

    Object class >> dependencies [
	"Answer a dictionary that associates an object with its dependents."

	<category: 'initialization'>
	^Dependencies
    ]

    Object class >> dependencies: anObject [
	"Use anObject as the dictionary that associates an object with its dependents."

	<category: 'initialization'>
	Dependencies := anObject
    ]

	initialize [
        "Subclasses should redefine this method to perform initializations on
        instance creation"
    ]

    class [
        "Answer the class to which the receiver belongs"
        <primitive: VMpr_Object_class>
        <category: 'builtin'>
        self primitiveFailed
    ]

    ~= anObject [
	"Answer whether the receiver and anObject are not equal"

	<category: 'relational operators'>
	^self = anObject == false
    ]

    ~~ anObject [
	"Answer whether the receiver and anObject are not the same object"

	<category: 'relational operators'>
	^self == anObject == false
    ]

    isKindOf: aClass [
	"Answer whether the receiver's class is aClass or
	 a subclass of aClass"

	<category: 'testing functionality'>
	^self class == aClass or: [self class inheritsFrom: aClass]
    ]

    isMemberOf: aClass [
	"Returns true if the receiver is an instance of the class 'aClass'"

	<category: 'testing functionality'>
	^self class == aClass
    ]

    respondsTo: aSymbol [
	"Returns true if the receiver understands the given selector"

	<category: 'testing functionality'>
	^self class canUnderstand: aSymbol
    ]

    isNil [
	"Answer whether the receiver is nil"

	<category: 'testing functionality'>
	^false
    ]

    notNil [
	"Answer whether the receiver is not nil"

	<category: 'testing functionality'>
	^true
    ]

    isCObject [
	<category: 'testing functionality'>
	^false
    ]

    isString [
	<category: 'testing functionality'>
	^false
    ]

    isCharacterArray [
	<category: 'testing functionality'>
	^false
    ]

    isSymbol [
	<category: 'testing functionality'>
	^false
    ]

    isCharacter [
	<category: 'testing functionality'>
	^false
    ]

    isNumber [
	<category: 'testing functionality'>
	^false
    ]

    isFloat [
	<category: 'testing functionality'>
	^false
    ]

    isInteger [
	<category: 'testing functionality'>
	^false
    ]

    isSmallInteger [
	<category: 'testing functionality'>
	^false
    ]

    isNamespace [
	<category: 'testing functionality'>
	^false
    ]

    isClass [
	<category: 'testing functionality'>
	^false
    ]

    isArray [
	<category: 'testing functionality'>
	^false
    ]

    isBehavior [
	<category: 'testing functionality'>
	^false
    ]

    isMeta [
	"Same as isMetaclass"

	<category: 'testing functionality'>
	^self isMetaclass
    ]

    isMetaClass [
	"Same as isMetaclass"

	<category: 'testing functionality'>
	^self isMetaclass
    ]

    isMetaclass [
	<category: 'testing functionality'>
	^false
    ]

    postCopy [
	"Performs any changes required to do on a copied object. This is the
	 place where one could, for example, put code to replace objects with
	 copies of the objects"

	<category: 'copying'>
	^self
    ]

    yourself [
	"Answer the receiver"

	<category: 'class type methods'>
	^self
    ]

    mourn [
	"This method is sent by the VM to weak and ephemeron objects when one of
	 their fields is found out to be garbage collectable (this means, for weak
	 objects, that there are no references to it from non-weak objects, and
	 for ephemeron objects, that the only paths to the first instance variable
	 pass through other instance variables of the same ephemeron).  The default
	 behavior is to do nothing."

	<category: 'finalization'>
	
    ]

    finalize [
	"Do nothing by default"

	<category: 'finalization'>
	
    ]

    changed [
	"Send update: for each of the receiver's dependents, passing them the
	 receiver"

	<category: 'change and update'>
	self changed: self
    ]
    displayOn: aStream [
	"Print a represention of the receiver on aStream. For most objects
	 this is simply its #printOn: representation, but for strings and
	 characters, superfluous dollars or extra pair of quotes are stripped."

	<category: 'printing'>
	self printOn: aStream
    ]

    postLoad [
	"Called after loading an object; must restore it to the state before
	 `preStore' was called.  Do nothing by default"

	<category: 'saving and loading'>
	
    ]

    postStore [
	"Called after an object is dumped; must restore it to the state before
	 `preStore' was called.  Call #postLoad by default"

	<category: 'saving and loading'>
	self postLoad
    ]

    preStore [
	"Called before dumping an object; it must *change* it (it must not answer
	 a new object) if necessary.  Do nothing by default"

	<category: 'saving and loading'>
	
    ]

    reconstructOriginalObject [
	"Used if an instance of the receiver's class is returned as the
	 #binaryRepresentationObject of another object.  The default implementation
	 raises an exception."

	<category: 'saving and loading'>
	self subclassResponsibility
    ]

    examine [
	"Print all the instance variables of the receiver on the Transcript"

	<category: 'debugging'>
        self examineOn: Transcript
    ]

    inspect [
	"In a GUI environment, this opens a tool to examine and modify the
	 receiver.  In the default image, it just calls #examine."

	<category: 'debugging'>
        self examineOn: Transcript
    ]

    validSize [
	"Answer how many elements in the receiver should be inspected"

	<category: 'debugging'>
	^self basicSize
    ]

    allOwners [
	"Return an Array of Objects that point to the receiver."

	<category: 'built ins'>
	<primitive: VMpr_Object_allOwners>
	
    ]

    changeClassTo: aBehavior [
	"Mutate the class of the receiver to be aBehavior.
	 Note: Tacitly assumes that the structure is the same
	 for the original and new class!!"

	<category: 'built ins'>
	<primitive: VMpr_Object_changeClassTo>
	
    ]

    at: anIndex [
	"Answer the index-th indexed instance variable of the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicAt>
	self checkIndexableBounds: anIndex
    ]

    basicAt: anIndex [
	"Answer the index-th indexed instance variable of the receiver.
	 This method must not be overridden, override at: instead"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicAt>
	self checkIndexableBounds: anIndex
    ]
	
    size [
	"Answer the number of indexed instance variable in the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicSize>
	
    ]

    basicSize [
	"Answer the number of indexed instance variable in the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicSize>
	
    ]

    becomeForward: otherObject [
	"Change all references to the receiver into references to otherObject.
	 References to otherObject are not transformed into the receiver.
	 Answer the receiver so that it is not lost."

	<category: 'built ins'>
	<primitive: VMpr_Object_becomeForward>
	^"SystemExceptions." ReadOnlyObject signal
    ]

    become: otherObject [
	"Change all references to the receiver into references to otherObject.
	 Depending on the implementation, references to otherObject might or
	 might not be transformed into the receiver (respectively,
	 'two-way become' and 'one-way become').
	 Implementations doing one-way become answer the receiver (so that it is
	 not lost). Most implementations doing two-way become answer otherObject,
	 but this is not assured - so do answer the receiver for consistency.
	 GNU Smalltalk does two-way become and answers otherObject, but this
	 might change in future versions: programs should not rely on the behavior
	 and results of #become: ."

	<category: 'built ins'>
	<primitive: VMpr_Object_become>
	^"SystemExceptions." ReadOnlyObject signal
    ]

    makeFixed [
	"Avoid that the receiver moves in memory across garbage collections."

	"We are an integer - fail"

	<category: 'built ins'>
	<primitive: VMpr_Object_makeFixed>
	"SystemExceptions." InvalidValue signalOn: self
	    reason: 'Instances of Integer cannot be tenured!'
    ]

    tenure [
	"Move the object to oldspace."

	"We are an integer - they won't notice the difference so don't
	 fail."

	<category: 'built ins'>
	<primitive: VMpr_Object_tenure>
	
    ]

    instVarNamed: aString [
	"Answer the instance variable named aString in the receiver."

	<category: 'introspection'>
	^self instVarAt: (self class indexOfInstVar: aString)
    ]

    instVarNamed: aString put: anObject [
	"Answer the instance variable named aString in the receiver."

	<category: 'introspection'>
	^self instVarAt: (self class indexOfInstVar: aString) put: anObject
    ]
	
    isReadOnly [
	"Answer whether the object's indexed instance variables can be
	 written"

	<category: 'built ins'>
	<primitive: VMpr_Object_isReadOnly>
	
    ]

    makeReadOnly: aBoolean [
	"Set whether the object's indexed instance variables can be written"

	<category: 'built ins'>
	<primitive: VMpr_Object_makeReadOnly>
	"SystemExceptions." WrongClass signalOn: aBoolean mustBe: Boolean
    ]

    makeWeak [
	"Make the object a 'weak' one. When an object is only referenced by weak
	 objects, it is collected and the slots in the weak objects are changed to
	 nils by the VM; the weak object is then sent the #mourn message."

	<category: 'built ins'>
	<primitive: VMpr_Object_makeWeak>
	
    ]

    makeEphemeron [
	"Make the object an 'ephemeron'.  An ephemeron is marked after all
	 other objects, and if no references are found to the key except from
	 the object itself, it is sent the #mourn message."

	<category: 'built ins'>
	<primitive: VMpr_Object_makeEphemeron>
	"SystemExceptions." InvalidValue signalOn: self
	    reason: 'ephemerons should have at least one instance variables'
    ]

    asOop [
	"Answer the object index associated to the receiver. The object
	 index doesn't change when garbage collection is performed."

	"We are an integer - fail"

	<category: 'built ins'>
	<primitive: VMpr_Object_hash>
	"SystemExceptions." InvalidValue signalOn: self
	    reason: 'Instances of Integer have no associated OOP!'
    ]

    identityHash [
	"Answer an hash value for the receiver. This method must not be
	 overridden"

	"We are an integer - answer the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_hash>
	^self
    ]

    hash [
	"Answer an hash value for the receiver. This hash value is ok
	 for objects that do not redefine ==."

	"We are an integer - answer the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_hash>
	^self
    ]

    nextInstance [
	"Private - answer another instance of the receiver's class, or
	 nil if the entire object table has been walked"

	<category: 'built ins'>
	<primitive: VMpr_Object_nextInstance>
	^nil
    ]
	
    == arg [
	"Answer whether the receiver is the same object as arg. This is a
	 very fast test and is called 'object identity'."

	<category: 'built ins'>
	<primitive: VMpr_Object_identity>
	
    ]

    = arg [
	"Answer whether the receiver is equal to arg. The equality test is
	 by default the same as that for identical objects. = must not fail;
	 answer false if the receiver cannot be compared to arg"

	<category: 'built ins'>
	<primitive: VMpr_Object_identity>
	
    ]

    class [
	"Answer the class to which the receiver belongs"

	<category: 'built ins'>
	<primitive: VMpr_Object_class>
	self primitiveFailed
    ]

    error: message [
	"Stop the execution and/or bring up a debugger. message is an error
	 message to be shown"

	<category: 'built ins'>
	<primitive: VMpr_Object_bootstrapError>
	
    ]

    basicPrint [
	"Print a basic representation of the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicPrint>
	
    ]

    halt [
	"Called to enter the debugger"

	<category: 'built ins'>
	^self halt: 'halt encountered'
    ]

    halt: aString [
	"Called to enter the debugger"

	<category: 'built ins'>
	^self error: aString
    ]

    mark: aSymbol [
	"Private - use this method to mark code which needs to be reworked,
	 removed, etc. You can then find all senders of #mark: to find all marked
	 methods or you can look for all senders of the symbol that you sent to
	 #mark: to find a category of marked methods."

	<category: 'built ins'>
	
    ]

    primitiveFailed [
	"Called when a VM primitive fails"

	<category: 'built ins'>
	"SystemExceptions." PrimitiveFailed signal
    ]

    shouldNotImplement [
	"Called when objects belonging to a class should not answer a
	 selector defined by a superclass"

	<category: 'built ins'>
	"SystemExceptions." ShouldNotImplement signal
    ]

    subclassResponsibility [
	"Called when a method defined by a class should be overridden
	 in a subclass"

	<category: 'built ins'>
	"SystemExceptions." SubclassResponsibility signal
    ]

    notYetImplemented [
	"Called when a method defined by a class is not yet implemented,
	 but is going to be"

	<category: 'built ins'>
	"SystemExceptions." NotYetImplemented signal
    ]

    doesNotUnderstand: message [
	"Called by the system when a selector was not found. message is a
	 Message containing information on the receiver"

	<category: 'VM callbacks'>
	<primitive: VMpr_Object_bootstrapDNU>
	
    ]

    badReturnError [
	"Called back when a block performs a bad return."

	<category: 'VM callbacks'>
	"SystemExceptions." BadReturn signal
    ]

    noRunnableProcess [
	"Called back when all processes are suspended"

	<category: 'VM callbacks'>
	"SystemExceptions." NoRunnableProcess signal
    ]

    userInterrupt [
	"Called back when the user presses Ctrl-Break"

	<category: 'VM callbacks'>
	"SystemExceptions." UserInterrupt signal
    ]
]

