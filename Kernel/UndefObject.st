"======================================================================
|
|   UndefinedObject (nil) Method Definitions
|
|
 ======================================================================"

"======================================================================
|
| Copyright 1988,92,94,95,99,2000,2001,2002,2003,2006,2008
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


Object subclass: UndefinedObject [
    
    <category: 'Language-Implementation'>
    <comment: 'I have the questionable distinction of being a class with only one
instance, which is the object "nil".'>
    <import: Smalltalk>
	
	copy [
	<category: 'basic'>
	^self
    ]

    shallowCopy [
	<category: 'basic'>
	^self
    ]

    deepCopy [
	<category: 'basic'>
	^self
    ]

    isNull [
	"Answer whether the receiver represents a NULL C pointer. Always
	 answer true."

	<category: 'testing'>
	^true
    ]

    isNil [
	"Answer whether the receiver is the undefined object nil. Always
	 answer true."

	<category: 'testing'>
	^true
    ]

    notNil [
	"Answer whether the receiver is not the undefined object nil. Always
	 answer false."

	<category: 'testing'>
	^false
    ]

    ifNil: nilBlock [
	"Evaluate nilBlock if the receiver is nil, else answer nil"

	<category: 'testing'>
	^nilBlock value
    ]

    ifNil: nilBlock ifNotNil: notNilBlock [
	"Evaluate nilBlock if the receiver is nil, else evaluate
	 notNilBlock, passing the receiver."

	<category: 'testing'>
	^nilBlock value
    ]

    ifNotNil: notNilBlock [
	"Evaluate notNilBlock if the receiver is not nil, passing the receiver.
	 Else answer nil"

	<category: 'testing'>
	^nil
    ]

    ifNotNil: notNilBlock ifNil: nilBlock [
	"Evaluate nilBlock if the receiver is nil, else evaluate
	 notNilBlock, passing the receiver."

	<category: 'testing'>
	^nilBlock value
    ]

    ifNil: nilBlock ifNotNilDo: iterableBlock [
	"Evaluate nilBlock if the receiver is nil, else evaluate
	 iterableBlock with each element of the receiver (which
         should be an Iterable)."

	<category: 'iteration'>
	^nilBlock value
    ]

    ifNotNilDo: iterableBlock [
	"Evaluate iterableBlock with each element of the receiver (which
         should be an Iterable) if not nil.  Else answer nil"

	<category: 'iteration'>
	^nil
    ]

    ifNotNilDo: iterableBlock ifNil: nilBlock [
	"Evaluate nilBlock if the receiver is nil, else evaluate
	 iterableBlock, passing each element of the receiver (which
         should be an Iterable)."

	<category: 'iteration'>
	^nilBlock value
    ]

    addDependent: ignored [
	"Fail, nil does not support dependents."

	<category: 'dependents access'>
	self shouldNotImplement
    ]

    release [
	"Ignore this call, nil does not support dependents."

	<category: 'dependents access'>
	
    ]

    printOn: aStream in: aNamespace [
	"Print on aStream a representation of the receiver as it would be accessed
	 from aNamespace: nil is the same everywhere, so print the same as
	 #printOn:"

	<category: 'printing'>
	aStream nextPutAll: 'nil'
    ]

    printOn: aStream [
	"Print a representation of the receiver on aStream."

	<category: 'printing'>
	aStream nextPutAll: 'nil'
    ]

    isLiteralObject [
	"Answer whether the receiver is expressible as a Smalltalk literal."

	<category: 'storing'>
	^true
    ]

    storeLiteralOn: aStream [
	"Store on aStream some Smalltalk code which compiles to the receiver"

	<category: 'storing'>
	self storeOn: aStream
    ]

    storeOn: aStream [
	"Store Smalltalk code compiling to the receiver on aStream."

	<category: 'storing'>
	self printOn: aStream
    ]
	
	subclass: classNameString environment: aNamespace [
	<category: 'class polymorphism'>
        ^(aNamespace at: classNameString)
    ]
]