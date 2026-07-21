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
		self 	testNewInit;
				testCopy;
				testMessage;
				testClass;
				testCharacter;
				testBlock;
				testSuper;
				testArray;
				testInteger;
				testObject;
				testFloat;
				testIterable;
				testByteArray;
				testCharArray;
				testString;
				testDictionary;
				testStream;
				testFileStream;
				testException
	]
	
	failBlk [
		"Block to run on test failure"
		^[self fail]
	]
	
	testNewInit [
		"Test basic object creation and initialization"
		| obj |
		obj := Object basicNew.
		obj notNil; size; isReadOnly.
		obj := Object basicNew: 10.
		obj notNil; size; isReadOnly.
		obj := Object new.
		obj notNil; size; isReadOnly.
		obj := Object new: 10.
		obj notNil; size; isReadOnly.
		#[4 5 6] size; isReadOnly.
		#(2 7 3) size; isReadOnly.
		'test string' size; isReadOnly.
		#testSymbol   size; isReadOnly.
	]
	
	testCopy [
		"Test Object copy and similar messages"
		| a1 a2 a3 a4 |
		a1 := (a3 := #(1 2 3)) copy.
		a2 := (a4 := #(4 5 6)) copy.
		(a1 == a3 or: [a2 == a4]) ifTrue: self failBlk.
		a2 become: a1.
		((a2 at: 1) ~= 1) ifTrue: self failBlk.
		((a1 at: 1) ~= 1) ifTrue: self failBlk.
	]
	
	testMessage [
		"Test Message objects"
		| m |
		m := Message selector: #at argument: 1.
		(m selector ~= #at) ifTrue: self failBlk.
		(m argument ~= 1)   ifTrue: self failBlk
	]
	
	testClass [
		"Test class behavior"
		(Collection isReadOnly) ifFalse: self failBlk.
		((Array new: 1) isReadOnly) ifTrue: self failBlk.
		TestSuite testClassVar: #(10 20 30).
		((TestSuite testClassVar at: 3) ~= 30) ifTrue: self failBlk.
		(true isKindOf: false class) ifTrue: self failBlk
	]
	
	testCharacter [
		"Test Character objects"
		($A isDigit: 16) ifFalse: self failBlk. ($E isVowel) ifFalse: self failBlk.
		(Character space isSeparator) ifFalse: self failBlk. 
		($! isPunctuation) ifFalse: self failBlk.
		($1 isDigit) ifFalse: self failBlk. ($8 isLetter) ifTrue: self failBlk. 
		($T isAlphaNumeric) ifFalse: self failBlk.
		($A asLowercase isUppercase) ifTrue: self failBlk.
		($b asUppercase isUppercase) ifFalse: self failBlk.
		($N = $r) ifTrue: [self fail]. ($X = $X) ifFalse: self failBlk.
		($J asString ~= 'J') ifTrue: self failBlk
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
		super isNil; notNil; isNil
	]
	
	testArray [
		"Test array types"
		| a b c x y |
		a := #[5 6 7 100].
		b := #([1 2 3] [8 9 10 11 23]).
		c := #(('abc' 'xyz') (1 2 9 7 3 19) 20).
		a := #(1 2 3 4 5).
		b := a copy.
		((b at: 1) ~= 1) ifTrue: self failBlk.
		((b at: 2) ~= 2) ifTrue: self failBlk.
		((b at: 3) ~= 3) ifTrue: self failBlk.
		b at: 3 put: 11.
		b at: 2 put: 3.
		((a at: 1) ~= 1) ifTrue: self failBlk.
		((a at: 2) ~= 2) ifTrue: self failBlk.
		((a at: 3) ~= 3) ifTrue: self failBlk.
		((b at: 1) ~= 1) ifTrue: self failBlk.
		((b at: 2) ~= 3) ifTrue: self failBlk.
		((b at: 3) ~= 11) ifTrue: self failBlk.
		y := #(1 2 3 4 10).
		x := Array new: y size.
		x replaceFrom: 1 to: x size with: y startingAt: 1.
		(a := Array new: 6 withAll: 10328) at: 2.
		^ #(1 2 3 'hello' false true nil #new)
	]
	
	testInteger [
		"Test integer types"
		| x y z |
		(5 scramble ~= 3423425485) ifTrue: self failBlk.
		((2 raisedTo: 3) ~= 8) ifTrue: self failBlk.
		((x := 100 / 10) ~= 10) ifTrue: self failBlk.
		((y := 1 / 3) isMemberOf: Fraction) ifFalse: self failBlk.
		z := SmallInteger largest.
		y := z bitShift: -30.
		x := ((16r10FF bitAnd: 16rB010) bitOr: 32) bitXor: 33.
		x := 139302 quo: -234.
		z := 1229 // 14.
		y := 1229 \\ 14.
		y := 1000 * 4 * 2.
		x := 1 + 2 - 100 + 105.
		(x < 4000 and: [x > 2]) ifFalse: self failBlk.
		(x >= 0 and: [x <= 8])  ifFalse: self failBlk.
		(x = 8 and: [x ~= 12359303]) ifFalse: self failBlk.
		1 / 4 * 2.
		((24 gcd: 32) ~= 8) ifTrue: [self fail]
	]
	
	testObject [
		"Test advanced features of Objects"
		| x y |
		((#(3 5 2) perform: #at: withArguments: #(2)) ~= 5) ifTrue: self failBlk.
		(nil perform: #isNil) ifFalse: self failBlk. 
		((Array perform: #new: with: 4) size ~= 4) ifTrue: self failBlk.
		x := Array basicNew: 3.
		y := Array basicNew: 2.
		x at: 1 put: y.
		(y allOwners size ~= 2) ifTrue: self failBlk
	]
	
	testFloat [
		"Test floating point types"
		| x |
		x := 12.4.
		(x exponent ~= 4) ifTrue: self failBlk.
		(x fractionPart closeTo: 0.4) ifFalse: self failBlk.
		(x truncated = 12) ifFalse: self failBlk.
		((x + 30 * 2) closeTo: 84.8) ifFalse: self failBlk.
		((x * (1 / 3)) closeTo: 4.133333) ifFalse: self failBlk.
		(x > 1) ifFalse: self failBlk.
		(x < 3043.24 and: [432.423 > x]) ifFalse: self failBlk.
		(x <= 12.4 and: [x >= 0.332]) ifFalse: self failBlk.
		(0.0 = 0.0 and: [x ~= 0.0]) ifFalse: self failBlk.
		Float e + 10.23 - 3.4e-5 * 5.74e3 / 8.43e9.
		FloatD fmax / 20.0e20 * 100000.0 * FloatD fminNormalized.
		FloatD infinity; negativeInfinity; nan; emax; emin; precision; decimalDigits
	]
	
	testIterable [
		"Test iterable types"
		| a |
		a := #(9 20 122 9 9 4 2 0 2 9 10 20 30 1).
		(a anySatisfy: [:elem | elem = 20]) ifFalse: self failBlk.
		(a allSatisfy: [:elem | elem < 10]) ifTrue:  self failBlk.
	   ((a count: 	   [:elem | elem = 9 ]) ~= 4) ifTrue: self failBlk
	]
		
	testByteArray [
		"Test byte array types"
		| a b x |
		a := #[1 2 3].
		(a = (b := a copy)) ifFalse: self failBlk.
		b at: 2 put: 10.
		((a at: 2) ~= 2) ifTrue: self failBlk.
		((b at: 2) ~= 10) ifTrue: self failBlk.
		(a = b) ifTrue: self failBlk.
		(#[116 101 115 116] asString ~= 'test') ifTrue: self failBlk.
		a := ByteArray with: 0 with: 4 with: 5.
		((a indexOf: 5 startingAt: 1) ~= 3) ifTrue: self failBlk.
		((a indexOf: 0 startingAt: 3) ~= 0) ifTrue: self failBlk.
		x := false.
		a indexOf: 10 startingAt: 1 ifAbsent: [x := true].
		(x ~~ true) ifTrue: self failBlk
	]
	
	testCharArray [
		| s |
		"Test character array types"
		('  mystr ' trimSeparators ~= 'mystr') ifTrue: self failBlk.
		('24' asInteger ~= 24) ifTrue: self failBlk.
		('##cde*' match: 'abcdefg') ifFalse: self failBlk.
		s := 'Another' copy.
		((s valueAt: 5) ~= 104) ifTrue: self failBlk.
		s valueAt: 1 put: $a value.
		(s = 'another') ifFalse: self failBlk.
		('hello1' asUppercase ~= 'HELLO1') ifTrue: self failBlk.
		('HELLO2' asLowercase ~= 'hello2') ifTrue: self failBlk.
		('3000' isNumeric) ifFalse: self failBlk.
		'This is a long example string' contractTo: 12
	]		
	
	testString [
		"Test string types"
		| s |
		s := 'andmorewords'.
		(s hash ~= 3235528494) ifTrue: self failBlk.
		('abc' , 'xyz' ~= 'abcxyz') ifTrue: self failBlk
		(s = 'andmorewords') ifFalse: self failBlk.
		((s indexOf: $d startingAt: 1) ~= 3) ifTrue: self failBlk.
		((s indexOf: $o startingAt: 6) ~= 9) ifTrue: self failBlk.
		((s indexOf: $x startingAt: 2) ~= 0) ifTrue: self failBlk.
		('test' asByteArray ~= #[116 101 115 116]) ifTrue: self failBlk
	]
	
	testDictionary [
		"Test dictionary types"
		| d b |
		d := Dictionary new.
		d add: 1000 -> 1.
		(d size ~= 1) ifTrue: self failBlk.
		d addAll: #[2 3 4].
		(d size ~= 4) ifTrue: self failBlk.
		((d at: 1) ~= 2) ifTrue: self failBlk.
		((d at: 2) ~= 3) ifTrue: self failBlk.
		((d at: 3) ~= 4) ifTrue: self failBlk.
		((d at: 1000) ~= 1) ifTrue: self failBlk.
		b := false.
		d at: 4 ifAbsent: [ b := true ].
		b ifFalse: self failBlk.
		(d values size ~= 4) ifTrue: self failBlk.
		(d includesKey: 2) ifFalse: self failBlk.
		(d includesKey: 5) ifTrue: self failBlk.
		(d includes: 2) ifFalse: self failBlk.
		(d includes: 10) ifTrue: self failBlk.
		((d occurrencesOf: 1) ~= 1) ifTrue: self failBlk.
		d removeKey: 3.
		(d size ~= 3) ifTrue: self failBlk.
		b := false.
		d removeKey: 11 ifAbsent: [ b := true ].
		b ifFalse: self failBlk.
		(d includesKey: 3) ifTrue: self failBlk
	]
	
	testStream [
		"Test stream types"
		| x s |
		s := 'This is a test write string'.
		x := WriteStream on: (Array new: 2).
		x nextPutAll: s.
		(x contents size ~= s size) ifTrue: self failBlk.
		x := ReadStream on: 'This is a test read string'.
		21 timesRepeat: [x next].
		(x peek ~= $t) ifTrue: self failBlk.
		x next: 2.
		(x peek ~= $i) ifTrue: self failBlk.
	]
	
	testFileStream [
		"Test file streams"
		(FileStream stdout == stdout) ifFalse: self failBlk.
		(FileStream stdin  == stdin)  ifFalse: self failBlk.
		(FileStream stderr == stderr) ifFalse: self failBlk
	]
	
	testException [
		"Test exception handling"
		Exception new
	]
]
