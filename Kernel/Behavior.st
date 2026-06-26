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
]
      