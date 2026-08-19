"=====================================================================
|
|   ObjectMemory method definitions
|
|
 ======================================================================"

"======================================================================
|
| Copyright 2001, 2002, 2003, 2005, 2006, 2008, 2009
| Free Software Foundation, Inc.
| Written by Paolo Bonzini.
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


Object subclass: ObjectMemory [
    | numObject numMethodSlab numMethodAlloc numBlockSlab numBlockAlloc numPyBlock |
    
    <category: 'Language-Implementation'>
    <comment: 'I provide a few methods that enable one to tune the
virtual machine''s usage of memory.  In addition, I can signal to my
dependants some `events'' that can happen during the virtual machine''s
life.

ObjectMemory has both class-side and instance-side methods.  In general,
class-side methods provide means to tune the parameters of the memory
manager, while instance-side methods are used together with the #current
class-side method to take a look at statistics on the memory manager''s
state.'>

    ObjectMemory class >> initialize [
	"Initialize the globals"

	"This method is called after all the kernel Smalltalk classes have been
	 loaded.  It generally performs any initializations that might depend on
	 the full Smalltalk class hierarchy being defined. After this is file is
	 loaded, some 'advanced' class definitions are loaded (CFuncs, Autoload,
	 exception handling, ...) and then the binary image is saved."

	<category: 'initialization'>
	self changed: #returnFromSnapshot
    ]

    ObjectMemory class >> current [
	"Return a snapshot of the VM's memory management statistics."

	<category: 'accessing'>
	^self new update
    ]

    ObjectMemory class >> compact [
	"Force a full garbage collection"

	<category: 'builtins'>
	<primitive: VMpr_ObjectMemory_compact>
	^self primitiveFailed
    ]

    ObjectMemory class >> abort [
	"Quit the Smalltalk environment, dumping core."

	<category: 'builtins'>
	<primitive: VMpr_ObjectMemory_abort>
	
    ]

    ObjectMemory class >> quit [
	"Quit the Smalltalk environment. Whether files are closed and
	 other similar cleanup occurs depends on the platform"

	<category: 'builtins'>
	self quit: 0
    ]

    ObjectMemory class >> quit: exitStatus [
	"Quit the Smalltalk environment, passing the exitStatus integer
	 to the OS. Files are closed and other similar cleanups occur."

	<category: 'builtins'>
	<primitive: VMpr_ObjectMemory_quit>
	"SystemExceptions." WrongClass signalOn: exitStatus mustBe: SmallInteger
    ]

    ObjectMemory class >> smoothingFactor [
	"Answer the factor (between 0 and 1) used to smooth the statistics
	 provided by the virtual machine about memory handling.  0 disables
	 updating the averages, 1 disables the smoothing (the statistics
	 return the last value)."

	<category: 'builtins'>
	<primitive: VMpr_ObjectMemory_getSmoothingFactor>
	^self primitiveFailed
    ]

    ObjectMemory class >> smoothingFactor: rate [
	"Set the factor (between 0 and 1) used to smooth the statistics
	 provided by the virtual machine about memory handling.  0 disables
	 updating the averages, 1 disables the smoothing (the statistics
	 return the last value)."

	<category: 'builtins'>
	<primitive: VMpr_ObjectMemory_setSmoothingFactor>
	rate class == FloatD 
	    ifTrue: 
		["SystemExceptions." ArgumentOutOfRange 
		    signalOn: rate
		    mustBeBetween: 0
		    and: 1]
	    ifFalse: [^self spaceGrowRate: rate asFloatD]
    ]

    ObjectMemory class >> primSnapshot: aString [
	"Save an image on the aString file"

	<category: 'private - builtins'>
	<primitive: VMpr_ObjectMemory_snapshot>
	^aString isString 
	    ifFalse: ["SystemExceptions." WrongClass signalOn: aString mustBe: String]
	    ifTrue: [File checkError]
    ]

    ObjectMemory class >> snapshot [
	"Save a snapshot on the image file that was loaded on startup."

	<category: 'saving the image'>
	^self primSnapshot: File image asString
    ]

    ObjectMemory class >> snapshot: aString [
	"Save an image on the aString file"

	<category: 'saving the image'>
	^self primSnapshot: aString asString
    ]

    ObjectMemory class >> gcMessage [
	"Answer whether messages indicating that garbage collection is taking
	 place are printed on stdout"

	<category: 'builtins'>
	^Smalltalk getTraceFlag: 3
    ]

    ObjectMemory class >> gcMessage: aBoolean [
	"Set whether messages indicating that garbage collection is taking
	 place are printed on stdout"

	<category: 'builtins'>
	^Smalltalk setTraceFlag: 3 to: aBoolean
    ]
	
	numObject [
	"Get the total number of objects"
	
	<category: 'accessing'>
	^numObject
	]
	
	numMethodSlab [
	"Get the number of MethodContext objects available in the slab"
	
	<category: 'accessing'>
	^numMethodSlab
	]
	
	numMethodAlloc [
	"Get the number of MethodContext slab allocations"
	
	<category: 'accessing'>
	^numMethodAlloc
	]
	
	numBlockSlab [
	"Get the number of BlockContext objects available in the slab"
	
	<category: 'accessing'>
	^numBlockSlab
	]
	
	numBlockAlloc [
	"Get the number of BlockContext slab allocations"
	
	<category: 'accessing'>
	^numMethodAlloc
	]
	
	numPyBlock [
	"Get the number of Python memory blocks allocated by the system"
	^numPyBlock
	]

    update [
	"Update the values in the object to the current state of the VM."

	<category: 'builtins'>
	<primitive: VMpr_ObjectMemory_update>
	self primitiveFailed
    ]
]

