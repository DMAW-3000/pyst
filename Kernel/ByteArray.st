"======================================================================
|
|   ByteArray Method Definitions
|
|
 ======================================================================"

"======================================================================
|
| Copyright 1988,92,94,95,99,2000,2001,2002,2006,2008,2009
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


ArrayedCollection subclass: ByteArray [
    
    <category: 'Collections-Sequenceable'>
    <comment: 'My instances are similar to strings in that they are both represented as
a sequence of bytes, but my individual elements are integers, where as
a String''s elements are characters.'>
	
	ByteArray class >> new: size [
	"Answer an empty ByteArray of size bytes"
	
	<category: 'instance creation'>
	<primitive: VMpr_ByteArray_newColonInitialize>
	WrongClass signalOn: size mustBe: SmallInteger
	]
	
	ByteArray class >> basicNew: size [
	"Answer an empty ByteArray of size bytes"
	
	<category: 'instance creation'>
	<primitive: VMpr_ByteArray_basicNewColon>
	WrongClass signalOn: size mustBe: SmallInteger
	]

    asString [
	"Answer a String whose character's ASCII codes are the receiver's contents"

	<category: 'converting'>
	| string size |
	size := self size.
	string := String new: size.
	string 
	    replaceFrom: 1
	    to: size
	    withByteArray: self
	    startingAt: 1.
	^string
    ]

    asUnicodeString [
	"Answer a UnicodeString whose character's codes are the receiver's contents.
	 This is not implemented unless you load the I18N package."

	<category: 'converting'>
	self shouldNotImplement
    ]

    isLiteralObject [
	"Answer whether the receiver is expressible as a Smalltalk literal."

	<category: 'storing'>
	^self isReadOnly not
    ]

    storeLiteralOn: aStream [
	"Put a Smalltalk literal evaluating to the receiver on aStream."

	<category: 'storing'>
	self class == ByteArray ifFalse: [ ^super storeLiteralOn: aStream ].
	aStream nextPut: $#.
	aStream nextPut: $[.
	self do: 
		[:elt | 
		aStream
		    print: elt;
		    space].
	aStream nextPut: $]
    ]

    storeOn: aStream [
	"Put Smalltalk code evaluating to the receiver on aStream."

	<category: 'storing'>
	self class == ByteArray ifFalse: [ ^super storeOn: aStream ].
	self storeLiteralOn: aStream.
	self isReadOnly ifFalse: [aStream nextPutAll: ' copy']
    ]

    at: anIndex ifAbsent: aBlock [
	"Answer the index-th indexed instance variable of the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicAt>
	^self checkIndexableBounds: anIndex ifAbsent: aBlock
    ]

    byteAt: index [
	"Answer the index-th indexed instance variable of the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicAt>
	self checkIndexableBounds: index
    ]

    byteAt: index put: value [
	"Store the `value' byte in the index-th indexed instance variable
	 of the receiver"

	<category: 'built ins'>
	<primitive: VMpr_Object_basicAtPut>
	self checkIndexableBounds: index put: value
    ]

    = aCollection [
	"Answer whether the receiver's items match those in aCollection"

	<category: 'basic'>
	<primitive: VMpr_ByteArray_equal>
	^false
    ]

    hash [
	"Answer an hash value for the receiver"

	<category: 'built ins'>
	<primitive: VMpr_String_hash>
	^0
    ]

    indexOf: anElement startingAt: anIndex ifAbsent: exceptionBlock [
	"Answer the first index > anIndex which contains anElement.
	 Invoke exceptionBlock and answer its result if no item is found"

	<category: 'basic'>
	<primitive: VMpr_ByteArray_indexOfStartingAt>
	"If anIndex is just past the end of the collection, don't raise
	 an error (this is the most generic solution that avoids that
	 #indexOf: fails when the collection is empty."
	^(anIndex < 1 or: [anIndex > (self size + 1)])
	    ifTrue: [self checkIndexableBounds: anIndex]
	    ifFalse: [exceptionBlock value]
    ]

    indexOf: anElement startingAt: anIndex [
	"Answer the first index > anIndex which contains anElement.
	 Invoke exceptionBlock and answer its result if no item is found"

	<category: 'basic'>
	<primitive: VMpr_ByteArray_indexOfStartingAt>
	"If anIndex is just past the end of the collection, don't raise
	 an error (this is the most generic solution that avoids that
	 #indexOf: fails when the collection is empty."
	^(anIndex < 1 or: [anIndex > (self size + 1)])
	    ifTrue: [self checkIndexableBounds: anIndex]
	    ifFalse: [0]
    ]

    replaceFrom: start to: stop withString: aString startingAt: replaceStart [
	"Replace the characters from start to stop with the
	 ASCII codes contained in aString (which, actually, can be
	 any variable byte class), starting at the replaceStart
	 location of aString"

	<category: 'built ins'>
	<primitive: VMpr_ByteArray_replaceFromToWithStringStartingAt>
	^super 
	    replaceFrom: start
	    to: stop
	    with: aString
	    startingAt: replaceStart
    ]

    replaceFrom: start to: stop with: aByteArray startingAt: replaceStart [
	"Replace the characters from start to stop with the
	 bytes contained in aByteArray (which, actually, can be
	 any variable byte class), starting at the replaceStart
	 location of aByteArray"

	<category: 'built ins'>
	<primitive: VMpr_ArrayedCollection_replaceFromToWithStartingAt>
	^super 
	    replaceFrom: start
	    to: stop
	    with: aByteArray
	    startingAt: replaceStart
    ]
]

