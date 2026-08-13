"======================================================================
|
|   pyst tests
|
|
 ======================================================================"
 
 Object subclass: TestSuite [
	| testInst1 testInst2 |
	
	TestClassVar := nil.
	
	TestSuite class >> testClassVar [
		^TestClassVar
	]
	
	TestSuite class >> testClassVar: val [
		TestClassVar := val
	]
	
	runAll [
		"Run all of the tests"
		'Running Kernel tests' displayNl.
		self 	testNewInit;
				testCopy;
				testMessage;
				testClass;
				testCharacter;
				testTime;
				testBlock;
				testSuper;
				testLink;
				testArray;
				testWeakArray;
				testInteger;
				testLargeInteger;
				testObject;
				testFloat;
				testFloatD;
				testFloatE;
				testFloatQ;
				testIterable;
				testByteArray;
				testCharArray;
				testString;
				testSymbol;
				testOrdCollection;
				testSortCollection;
				testSet;
				testDictionary;
				testLookupTable;
				testNamespace;
				testWeakSet;
				testWeakKeyDict;
				testStream;
				testFileStream;
				testException
	]
	
	initialize [
		"Setup test initial state"
		testInst1 := testInst2 := 0
	]
	
	failBlk [
		"Block to run on test failure"
		^[self fail]
	]
	
	isNil [
		"Override for testing send to super"
		TestClassVar := true.
		^super isNil
	]
	
	testNewInit [
		"Test basic object creation and initialization"
		| obj |
		(testInst1 isNil or: [ testInst2 isNil ]) ifTrue: self failBlk.
		obj := Object basicNew.
		obj notNil ifFalse: self failBlk.
		obj size ~= 0 ifTrue: self failBlk.
		obj isReadOnly ifTrue: self failBlk.
		obj := Object basicNew: 10.
		obj notNil ifFalse: self failBlk.
		obj size ~= 10 ifTrue: self failBlk.
		obj isReadOnly ifTrue: self failBlk.
		obj := Object new.
		obj notNil ifFalse: self failBlk.
		obj size ~= 0 ifTrue: self failBlk.
		obj isReadOnly ifTrue: self failBlk.
		obj := Object new: 10.
		obj notNil ifFalse: self failBlk.
		obj size ~= 10 ifTrue: self failBlk.
		obj isReadOnly ifTrue: self failBlk.
		obj := #[4 5 6].
		obj size ~= 3 ifTrue: self failBlk.
		obj isReadOnly ifFalse: self failBlk.
		obj := #(2 7 3).
		obj size ~= 3 ifTrue: self failBlk.
		obj isReadOnly ifFalse: self failBlk.
		obj := 'test string'.
		obj size ~= 11 ifTrue: self failBlk.
		obj isReadOnly ifFalse: self failBlk.
		obj := #testSymbol.
		obj size ~= 10 ifTrue: self failBlk.
		obj isReadOnly ifFalse: self failBlk.
		obj ~= obj yourself ifTrue: self failBlk
	]
	
	testCopy [
		"Test Object copy and similar messages"
		| a1 a2 a3 a4 |
		a1 := (a3 := #(1 2 3)) copy.
		a2 := (a4 := #(4 5 6)) copy.
		(a1 == a3 or: [a2 == a4]) ifTrue: self failBlk.
		a2 become: a1.
		(a2 at: 1) ~= 1 ifTrue: self failBlk.
		(a1 at: 1) ~= 1 ifTrue: self failBlk.
	]
	
	testMessage [
		"Test Message objects"
		| m |
		m := Message selector: #at: argument: 1.
		m selector ~= #at: ifTrue: self failBlk.
		m argument ~= 1    ifTrue: self failBlk.
		(#(5 6 7) perform: m) ~= 5) ifTrue: self failBlk
	]
	
	testClass [
		"Test class behavior"
		(Character indexOfInstVar: 'codePoint') ~= 1 ifTrue: self failBlk.
		(Character allInstVarNames at: 1) ~= 'codePoint' ifTrue: self failBlk.
		('hello' respondsTo: #indexOf:startingAt:) ifFalse: self failBlk.
		(Object lookupSelector: #isString) notNil ifFalse: self failBlk.
		(Object >> #isString isMemberOf: CompiledMethod) ifFalse: self failBlk.
		Object hasMethods ifFalse: self failBlk.
		(Integer allSuperclasses includes: Magnitude) ifFalse: self failBlk.
		(Object subclasses includes: Magnitude) ifFalse: self failBlk.
		Magnitude superclass ~= Object ifTrue: self failBlk.
		Collection isReadOnly ifFalse: self failBlk.
		((Array new: 1) isReadOnly) ifTrue: self failBlk.
		TestSuite testClassVar: #(10 20 30).
		((TestSuite testClassVar at: 3) ~= 30) ifTrue: self failBlk.
		(true isKindOf: false class) ifTrue: self failBlk
	]
	
	testCharacter [
		"Test Character objects"
		($A isDigit: 16) ifFalse: self failBlk. $E isVowel ifFalse: self failBlk.
		Character space isSeparator ifFalse: self failBlk. 
		$! isPunctuation ifFalse: self failBlk.
		$1 isDigit ifFalse: self failBlk. ($8 isLetter) ifTrue: self failBlk. 
		$T isAlphaNumeric ifFalse: self failBlk.
		$A asLowercase isUppercase ifTrue: self failBlk.
		$b asUppercase isUppercase ifFalse: self failBlk.
		$N = $r ifTrue: [self fail]. ($X = $X) ifFalse: self failBlk.
		$J asString ~= 'J' ifTrue: self failBlk.
		$2 copy ~~ $2 ifTrue: self failBlk
	]
	
	testTime [
		"Test time and duration types"
		| t |
		t := Time now.
		Time utcNow > t ifFalse: self failBlk.
		Time timezone isString ifFalse: self failBlk.
		t := Duration days: 3.
		t positive ifFalse: self failBlk.
		t days ~= 3 ifTrue: self failBlk.
		t := t + (Duration days: 2).
		t days ~= 5 ifTrue: self failBlk
	]
		
	testBlock [
        "Test block closures"
		([:x | true and: [x]] value: false) ifTrue: self failBlk.
		([:x | true and: [x]] cull: false cull: false) ifTrue: self failBlk.
		(([:x :y :z | x + y - z ] valueWithArguments: #(5 22 7)) ~= 20) ifTrue: self failBlk.
		true ifTrue: [ | r s | r := false. s := true].
		[:a | | x | x := a] value: #nil
    ]
	
	testSuper [
		"Test super messages"
		TestClassVar := false.
		self isNil ifTrue: self failBlk.
		TestClassVar ifFalse: self failBlk
	]
	
	testLink [
		"Test Link objects"
		| link1 link2 link3 |
		link3 := Link new.
		link2 := Link nextLink: link3.
		link1 := Link nextLink: link2.
		link1 size ~= 3 ifTrue: self failBlk
	]
	
	testArray [
		"Test array types"
		| a b c x y |
		a := #(#testSymbol).
		(a at: 1) == #testSymbol ifFalse: self failBlk.
		a := #[5 6 7 100].
		b := #([1 2 3] [8 9 10 11 23]).
		c := #(('abc' 'xyz') (1 2 9 7 3 19) 20).
		a := #(1 2 3 4 5).
		b := a copy.
		(b at: 1) ~= 1 ifTrue: self failBlk.
		(b at: 2) ~= 2 ifTrue: self failBlk.
		(b at: 3) ~= 3 ifTrue: self failBlk.
		b at: 3 put: 11.
		b at: 2 put: 3.
		(a at: 1) ~= 1 ifTrue: self failBlk.
		(a at: 2) ~= 2 ifTrue: self failBlk.
		(a at: 3) ~= 3 ifTrue: self failBlk.
		(b at: 1) ~= 1 ifTrue: self failBlk.
		(b at: 2) ~= 3 ifTrue: self failBlk.
		(b at: 3) ~= 11 ifTrue: self failBlk.
		y := #(1 2 3 4 10).
		x := Array new: y size.
		x replaceFrom: 1 to: x size with: y startingAt: 1.
		(a := Array new: 6 withAll: 10328) at: 2.
		^ #(1 2 3 'hello' false true nil #new)
	]
	
	testWeakArray [
		"Test weak array types"
		| arr1 arr2 obj1 obj2 |
		obj1 := Object new: 1. obj2 := Object new: 2. 
		arr1 := WeakArray with: obj1 with: obj2.
		arr2 := WeakArray with: obj1 with: obj2.
		(arr1 size ~= 2 or: [ arr2 size ~= 2 ]) ifTrue: self failBlk.
		((arr1 at: 1) ~~ obj1) ifTrue: self failBlk.
		(arr2 anySatisfy: [:elem | elem == nil ]) ifTrue: self failBlk.
		arr2 at: 1 put: nil.
		(arr2 at: 1) isNil ifFalse: self failBlk.
		(arr2 isAlive: 1) ifFalse: self failBlk.
		arr1 asArray size ~= 2 ifTrue: self failBlk
	]
	
	testInteger [
		"Test integer types"
		| x y z |
		'-1234' asInteger ~= -1234 ifTrue: self failBlk.
		(1240 printString ~= '1240') ifTrue: self failBlk.
		5 hash ~= 5 ifTrue: self failBlk.
		5 scramble ~= 3423425485 ifTrue: self failBlk.
		(2 raisedTo: 3) ~= 8 ifTrue: self failBlk.
		(x := 100 / 10) ~= 10 ifTrue: self failBlk.
		((y := 1 / 3) isMemberOf: Fraction) ifFalse: self failBlk.
		z := SmallInteger largest.
		y := z bitShift: -30.
		x := ((16r10FF bitAnd: 16rB010) bitOr: 32) bitXor: 33.
		x := 139302 quo: -234.
		z := 1229 // 14.
		y := 1229 \\ 14.
		(y := 1000 * 4 * 2) ~= 8000 ifTrue: self failBlk.
		x := 1 + 2 - 100 + 105.
		(x < 4000 and: [x > 2]) ifFalse: self failBlk.
		(x >= 0 and: [x <= 8])  ifFalse: self failBlk.
		(x = 8 and: [x ~= 12359303]) ifFalse: self failBlk.
		x isLiteralObject ifFalse: self failBlk.
		x isExact ifFalse: self failBlk.
		1 / 4 * 2.
		((24 gcd: 32) ~= 8) ifTrue: [self fail]
	]
	
	testLargeInteger [
		"Test LargeInteger types"
		| x |
		x := 123454578652891329324 negated.
		x hash ~= 2375325300 ifTrue: self failBlk.
		(x asFloat closeTo: -1.2345457865289133d20) ifFalse: self failBlk.
		x := SmallInteger largest + 10.
		x negative ifTrue: self failBlk.
		x printString ~= '9223372036854775817' ifTrue: self failBlk.
		x := SmallInteger largest negated - 10.
		x negative ifFalse: self failBlk.
		x := SmallInteger largest * 10.
		x negative ifTrue: self failBlk.
		x ~= 92233720368547758070 ifTrue: self failBlk.
		x := SmallInteger largest negated * -10.
		x negative ifTrue: self failBlk.
		x := x * 100 // 10.
		x ~= 922337203685477580700 ifTrue: self failBlk.
		x \\ 10 ~= 0 ifTrue: self failBlk .
		(x > 1000 and: [x - 1 < x]) ifFalse: self failBlk.
		(x >= 2 and: [x >= x]) ifFalse: self failBlk.
		x = 922337203685477580700 ifFalse: self failBlk.
		(x bitAnd: 1) ~= 0 ifTrue: self failBlk.
		(x bitOr: 1) ~= 922337203685477580701 ifTrue: self failBlk.
		(x bitXor: 1) ~= 922337203685477580701 ifTrue: self failBlk.
		(x bitShift: -1) ~= (922337203685477580700 // 2) ifTrue: self failBlk.
		(x bitShift: 1) ~= (922337203685477580700 * 2) ifTrue: self failBlk
	]
	
	testObject [
		"Test advanced features of Objects"
		| x y |
		x := Object new.
		x dependents size ~= 0 ifTrue: self failBlk.
		y := 'xyz'. x addDependent: y.
		x dependents size ~= 1 ifTrue: self failBlk.
		x changed: true.
		x broadcast: #isNil.
		self testObject1.
		x removeDependent: y.
		x dependents size ~= 0 ifTrue: self failBlk.
		(#(3 5 2) perform: #at: withArguments: #(2)) ~= 5 ifTrue: self failBlk.
		(nil perform: #isNil) ifFalse: self failBlk. 
		((Array perform: #new: with: 4) size ~= 4) ifTrue: self failBlk.
		x := Array basicNew: 3.
		y := Array basicNew: 2.
		x at: 1 put: y.
		(y allOwners size ~= 2) ifTrue: self failBlk.
		x := Association key: 1 value: 2.
		(x instVarAt: 2) ~= 2 ifTrue: self failBlk.
		(x instVarNamed: 'key') ~= 1 ifTrue: self failBlk.
		x instVarAt: 1 put: 10; instVarNamed: 'value' put: 20.
		x key ~= 10 ifTrue: self failBlk.
		x value ~= 20 ifTrue: self failBlk.
	]
	
	testObject1 [
		"Test advanced features of Objects"
		(Object new: 1) addToBeFinalized
	]		
	
	testFloat [
		"Test generic floating point types"
		| x |
		x := Number readFrom: '1.4324' readStream.
		(x closeTo: 1.4324) ifFalse: self failBlk.
		((2.0 raisedTo: 3.0) closeTo: 8.0) ifFalse: self failBlk.
		x := Float e.
		(0.0 exp closeTo: 1.0) ifFalse: self failBlk.
		(1 exp closeTo: x) ifFalse: self failBlk.
		(1 ln closeTo: 0.0) ifFalse: self failBlk.
		(x ln closeTo: 1.0) ifFalse: self failBlk.
		(x sqrt * x sqrt closeTo: x) ifFalse: self failBlk.
		(10.0 log closeTo: 1.0) ifFalse: self failBlk.
		(100 log closeTo: 2.0) ifFalse: self failBlk.
		x := Float pi / 2.
		(x sin closeTo: 1.0) ifFalse: self failBlk.
		(0 sin closeTo: 0.0) ifFalse: self failBlk.
		(x cos closeTo: 0.0) ifFalse: self failBlk.
		(0 cos closeTo: 1.0) ifFalse: self failBlk.
		((x / 2) tan closeTo: 1.0) ifFalse: self failBlk.
		(0 tan closeTo: 0.0) ifFalse: self failBlk.
		(0.0 arcSin closeTo: 0.0) ifFalse: self failBlk.
		(1 arcSin closeTo: x) ifFalse: self failBlk.
		(0.0 arcCos closeTo: x) ifFalse: self failBlk.
		(1 arcCos closeTo: 0.0) ifFalse: self failBlk.
		(0.0 arcTan closeTo: 0.0) ifFalse: self failBlk.
		(0.0 sinh closeTo: 0.0) ifFalse: self failBlk.
		(0.0 cosh closeTo: 1.0) ifFalse: self failBlk.
		(0.0 tanh closeTo: 0.0) ifFalse: self failBlk.
		x := -233.23.
		x printString ~= '-233.23' ifTrue: self failBlk.
		x negative ifFalse: self failBlk.
		x positive ifTrue: self failBlk.
		x strictlyPositive ifTrue: self failBlk.
		0.0 positive ifFalse: self failBlk.
		(x abs closeTo: x negated) ifFalse: self failBlk.
		x asExactFraction isExact ifFalse: self failBlk.
		x hash isInteger ifFalse: self failBlk.
		1.0 hash ~= 1 ifTrue: self failBlk.
		(x rounded closeTo: -233.0) ifFalse: self failBlk.
		(x half closeTo: 0.5) ifFalse: self failBlk.
		x floor ~= -234 ifTrue: self failBlk.
		x ceiling ~= -233 ifTrue: self failBlk.
		x isExact ifTrue: self failBlk.
		x isLiteralObject ifFalse: self failBlk.
		((1.443 min: 2.321) closeTo: 1.443) ifFalse: self failBlk.
		((-2.323 max: -3.234) closeTo: -2.323) ifFalse: self failBlk
	]
	
	testFloatD [
		"Test double precision floating point types"
		| x |
		(FloatD fromBytes: (ByteArray new: 8)) ~= 0.0 ifTrue: self failBlk.
		FloatD signByte ~= 1 ifTrue: self failBlk.
		x := 12.4d0.
		x asBytes size ~= 8 ifTrue: self failBlk.
		x exponent ~= 4 ifTrue: self failBlk.
		(x fractionPart closeTo: 0.4) ifFalse: self failBlk.
		(x truncated = 12) ifFalse: self failBlk.
		((x + 30 * 2) closeTo: 84.8) ifFalse: self failBlk.
		((x * (1 / 3)) closeTo: 4.133333) ifFalse: self failBlk.
		(x > 1) ifFalse: self failBlk.
		(x < 3043.24 and: [432.423 > x]) ifFalse: self failBlk.
		(x <= 12.4 and: [x >= 0.332]) ifFalse: self failBlk.
		(0.0 = 0.0 and: [x ~= 0.0]) ifFalse: self failBlk.
		Float e + 10.23 - 3.4d-5 * 5.74d3 / 8.43d9.
		FloatD fmax / 20.0d20 * 100000.0 * FloatD fminNormalized.
		FloatD nan; decimalDigits.
		FloatD precision ~= 53 ifTrue: self failBlk.
		FloatD emin ~= -1022 ifTrue: self failBlk.
		FloatD emax ~= 1023 ifTrue: self failBlk.
		1.0d200 * 1.0d200 ~= FloatD infinity ifTrue: self failBlk.
		-1.0d200 * 1.0d200 ~= FloatD negativeInfinity ifTrue: self failBlk.
		FloatD infinity printString ~= 'Inf' ifTrue: self failBlk.
		FloatD negativeInfinity printString ~= '-Inf' ifTrue: self failBlk.
		FloatD nan printString ~= 'NaN' ifTrue: self failBlk
	]
	
	testFloatE [
		"Test single precision floating point types"
		| x |
		x := 3.53e-2.
		FloatE fmax; fminNormalized.
		x fractionPart.
		x exponent ~= 122 ifTrue: self failBlk.
		x asBytes size ~= 4 ifTrue: self failBlk.
		FloatE signByte ~= 1 ifTrue: self failBlk.
		FloatE fromBytes: (ByteArray new: 4).
		FloatE infinity; negativeInfinity; nan; decimalDigits.
		FloatE emin ~= -126 ifTrue: self failBlk.
		FloatE emax ~= 127 ifTrue: self failBlk.
		FloatE precision ~= 24 ifTrue: self failBlk
	]
	
	testFloatQ [
		"Test quad precision floating point types"
		| x |
		x := 3.5347301894q20
	]
	
	testIterable [
		"Test iterable types"
		| a |
		a := #(9 20 122 9 9 4 2 0 2 9 10 20 30 1).
		(a anySatisfy: [:elem | elem = 20]) ifFalse: self failBlk.
		(a allSatisfy: [:elem | elem < 10]) ifTrue:  self failBlk.
	    (a count: 	   [:elem | elem = 9 ]) ~= 4 ifTrue: self failBlk
	]
		
	testByteArray [
		"Test byte array types"
		| a b x |
		a := #[1 2 3].
		a = (b := a copy) ifFalse: self failBlk.
		b at: 2 put: 10.
		(a at: 2) ~= 2 ifTrue: self failBlk.
		(b at: 2) ~= 10 ifTrue: self failBlk.
		a = b ifTrue: self failBlk.
		#[116 101 115 116] asString ~= 'test' ifTrue: self failBlk.
		a := ByteArray with: 0 with: 4 with: 5.
		(a indexOf: 5 startingAt: 1) ~= 3 ifTrue: self failBlk.
		(a indexOf: 0 startingAt: 3) ~= 0 ifTrue: self failBlk.
		x := false.
		a indexOf: 10 startingAt: 1 ifAbsent: [x := true].
		x ifFalse: self failBlk
	]
	
	testCharArray [
		| s |
		"Test character array types"
		'  mystr ' trimSeparators ~= 'mystr' ifTrue: self failBlk.
		'24' asInteger ~= 24 ifTrue: self failBlk.
		('##cde*' match: 'abcdefg') ifFalse: self failBlk.
		s := 'Another' copy.
		(s valueAt: 5) ~= 104 ifTrue: self failBlk.
		s valueAt: 1 put: $a value.
		s = 'another' ifFalse: self failBlk.
		'hello1' asUppercase ~= 'HELLO1' ifTrue: self failBlk.
		'HELLO2' asLowercase ~= 'hello2' ifTrue: self failBlk.
		'3000' isNumeric) ifFalse: self failBlk.
		'This is a long example string' contractTo: 12
	]		
	
	testString [
		"Test string types"
		| s |
		s := 'andmorewords'.
		s isString ifFalse: self failBlk.
		s hash ~= 3235528494 ifTrue: self failBlk.
		'abc' , 'xyz' ~= 'abcxyz' ifTrue: self failBlk.
		s = 'andmorewords' ifFalse: self failBlk.
		(s indexOf: $d startingAt: 1) ~= 3 ifTrue: self failBlk.
		(s indexOf: $o startingAt: 6) ~= 9 ifTrue: self failBlk.
		(s indexOf: $x startingAt: 2) ~= 0 ifTrue: self failBlk.
		'test' asByteArray ~= #[116 101 115 116] ifTrue: self failBlk
	]
	
	testSymbol [
		"Test Symbols"
		| s b |
		(Symbol isSymbolString: 'testSymbol') ifFalse: self failBlk.
		b := false.
		Symbol hasInterned: 'testSymbol' ifTrue: [:sym | b := true ].
		b ifFalse: self failBlk.
		s := 'aNewSymbol' asSymbol.
		s isReadOnly ifFalse: self failBlk.
		s := #testSymbol.
		s asString ~= 'testSymbol' ifTrue: self failBlk.
		s copy ~~ s ifTrue: self failBlk.
		s isSymbol ifFalse: self failBlk.
		s isString ifTrue: self failBlk.
		s ~~ #testSymbol ifTrue: self failBlk.
		s numArgs ~= 0 ifTrue: self failBlk.
		s hash = 'testSymbol' hash ifTrue: self failBlk
	]
	
	testOrdCollection [
		"Test OrderedCollection"
		| c |
		c := OrderedCollection new.
		c add: 3; add: 4.
		c first ~= 3 ifTrue: self failBlk.
		c last ~= 4 ifTrue: self failBlk.
		c size ~= 2 ifTrue: self failBlk.
		c add: 1 before: 3.
		c first ~= 1 ifTrue: self failBlk.
		c addFirst: 0.
		c first ~= 0 ifTrue: self failBlk.
		c removeLast.
		c last ~= 3 ifTrue: self failBlk.
		(c indexOf: 1) ~= 2 ifTrue: self failBlk.
		c removeFirst.
		c size ~= 2 ifTrue: self failBlk.
		c addAll: #(3 4 5 6 6 8 9 2 3 2 3).
		c size ~= 13 ifTrue: self failBlk
	]
	
	testSortCollection [
		"Test SortedCollection"
		| c |
		c := SortedCollection new.
		c size ~= 0 ifTrue: self failBlk.
		c := #(2 4 1 0 4 9 3) asSortedCollection.
		(c at: 1) ~= 0 ifTrue: self failBlk.
		(c at: 2) ~= 1 ifTrue: self failBlk.
		c last ~= 9 ifTrue: self failBlk.
		(c occurrencesOf: 4) ~= 2 ifTrue: self failBlk.
		(c includes: 1) ifFalse: self failBlk.
		(c includes: 10) ifTrue: self failBlk.
		c := #(4 2 0) sorted.
		c ~= #(0 2 4) ifFalse: self failBlk
	]
	
	testSet [
		"Test set types"
		| s t b |
		s := Set new.
		s add: 'abc'.
		s size ~= 1 ifTrue: self failBlk.
		t := s copy.
		t add: 'def'.
		t size ~= 2 ifTrue: self failBlk.
		(t includes: 'def') ifFalse: self failBlk.
		(s includes: 'def') ifTrue:  self failBlk.
		t > s  ifFalse: self failBlk.
		t >= t ifFalse: self failBlk.
		t + s ~= t ifTrue: self failBlk.
		t & s ~= s ifTrue: self failBlk.
		(t - s) size ~= 1 ifTrue: self failBlk.
		t remove: 'def'.
		(t includes: 'def') ifTrue: self failBlk.
		b := false.
		t remove: 'def' ifAbsent: [ b := true ].
		b ifFalse: self failBlk
	]
	
	testDictionary [
		"Test dictionary types"
		| d b |
		d := Dictionary new.
		d add: 1000 -> 1.
		d size ~= 1 ifTrue: self failBlk.
		d addAll: #[2 3 4].
		d size ~= 4 ifTrue: self failBlk.
		(d at: 1) ~= 2 ifTrue: self failBlk.
		(d at: 2) ~= 3 ifTrue: self failBlk.
		(d at: 3) ~= 4 ifTrue: self failBlk.
		(d at: 1000) ~= 1 ifTrue: self failBlk.
		b := false.
		d at: 4 ifAbsent: [ b := true ].
		b ifFalse: self failBlk.
		d values size ~= 4 ifTrue: self failBlk.
		(d includesKey: 2) ifFalse: self failBlk.
		(d includesKey: 5) ifTrue: self failBlk.
		(d includes: 2) ifFalse: self failBlk.
		(d includes: 10) ifTrue: self failBlk.
		(d occurrencesOf: 1) ~= 1 ifTrue: self failBlk.
		(d removeKey: 3) ~= 4 ifTrue: self failBlk.
		d size ~= 3 ifTrue: self failBlk.
		b := false.
		d removeKey: 11 ifAbsent: [ b := true ].
		b ifFalse: self failBlk.
		(d includesKey: 3) ifTrue: self failBlk
	]
	
	testLookupTable [
		"Test lookup table types"
		| d b |
		d := LookupTable new.
		d at: 1 put: 1000.
		d at: 2 put: 2000.
		d at: 3 put: 3000.
		d at: 4 put: 4000.
		d at: 5 put: 5000.
		d at: 6 put: 6000.
		d at: 7 put: 7000.
		d size ~= 7 ifTrue: self failBlk.
		(d at: 2) ~= 2000 ifTrue: self failBlk.
		(d removeKey: 4) ~= 4000 ifTrue: self failBlk.
		d size ~= 6 ifTrue: self failBlk.
		b := false.
		d keysDo: [:key | key = 2 ifTrue: [ b := true ]].
		b ifFalse: self failBlk
	]
	
	testNamespace [
		"Test the global Smalltalk namespace"
		| n |
		n := Smalltalk.
		n size.
		n at: #NewSymbol put: 1.
		NewSymbol ~= 1 ifTrue: self failBlk.
		n at: #KernelInitialized put: true.
		KernelInitialized ifFalse: self failBlk.
		(n at: #KernelInitialized) ifFalse: self failBlk.
		KernelInitialized := false.
		(n at: #KernelInitialized) ifTrue: self failBlk.
		(n at: #stdout) class ~= FileStream ifTrue: self failBlk.
	]
	
	testWeakSet [
		"Test weak sets"
		| s key1 |
		s := WeakSet new.
		s add: (key1 := 'abc' copy).
		s size ~= 1 ifTrue: self failBlk.
		(s includes: key1) ifFalse: self failBlk
	]
		
	
	testWeakKeyDict [
		"Test weak key dictionaries"
		| d key1 key2 |
		d := WeakKeyDictionary new.
		key1 := 'ab' copy. key2 := 'cd' copy.
		d add: key1 -> 1.
		d add: key2 -> 2
	]
	
	testStream [
		"Test stream types"
		| x s |
		s := 'This is a test write string'.
		x := WriteStream on: (Array new: 2).
		x nextPutAll: s.
		x contents size ~= s size ifTrue: self failBlk.
		x := ReadStream on: 'This is a test read string'.
		21 timesRepeat: [x next].
		x peek ~= $t ifTrue: self failBlk.
		x next: 2.
		x peek ~= $i ifTrue: self failBlk.
		10 timesRepeat: [x next].
	]
	
	testFileStream [
		"Test file streams"
		FileStream stdout == stdout ifFalse: self failBlk.
		FileStream stdin  == stdin  ifFalse: self failBlk.
		FileStream stderr == stderr ifFalse: self failBlk.
		stdin  isOpen ifFalse: self failBlk.
		stdout isOpen ifFalse: self failBlk.
		stderr isOpen ifFalse: self failBlk
	]
	
	testException [
		"Test exception handling"
		Exception new
	]
]
