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
				testStream;
				testException
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
		| a1 a2 |
		a1 := #(1 2 3) copy.
		a2 := #(4 5 6) copy.
		a2 become: a1.
		((a2 at: 1) ~= 1) ifTrue: [self fail].
		((a1 at: 1) ~= 1) ifTrue: [self fail].
	]
	
	testClass [
		"Test class behavior"
		(Collection isReadOnly) ifFalse: [self fail].
		((Array new: 1) isReadOnly) ifTrue: [self fail].
		TestSuite testClassVar: #(10 20 30).
		((TestSuite testClassVar at: 3) ~= 30) ifTrue: [self fail].
		(true isKindOf: false class) ifTrue: [self fail]
	]
	
	testCharacter [
		"Test Character objects"
		($A isDigit: 16) ifFalse: [self fail]. ($E isVowel) ifFalse: [self fail].
		(Character space isSeparator) ifFalse: [self fail]. 
		($! isPunctuation) ifFalse: [self fail].
		($1 isDigit) ifFalse: [self fail]. ($8 isLetter) ifTrue: [self fail]. 
		($T isAlphaNumeric) ifFalse: [self fail].
		($A asLowercase isUppercase) ifTrue: [self fail].
		($b asUppercase isUppercase) ifFalse: [self fail].
		($N = $r) ifTrue: [self fail]. ($X = $X) ifFalse: [self fail]
	]
		
	testBlock [
        "Test block closures"
		([:x | true and: [x]] value: false) ifTrue: [self fail].
		([:x | true and: [x]] cull: false cull: false) ifTrue: [self fail].
		(([:x :y :z | x + y - z ] valueWithArguments: #(5 22 7)) ~= 20) ifTrue: [self fail].
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
		((b at: 1) ~= 1) ifTrue: [self fail].
		((b at: 2) ~= 2) ifTrue: [self fail].
		((b at: 3) ~= 3) ifTrue: [self fail].
		b at: 3 put: 11.
		b at: 2 put: 3.
		((b at: 1) ~= 1) ifTrue: [self fail].
		((b at: 2) ~= 3) ifTrue: [self fail].
		((b at: 3) ~= 11) ifTrue: [self fail].
		y := #(1 2 3 4 10).
		x := Array new: y size.
		x replaceFrom: 1 to: x size with: y startingAt: 1.
		(a := Array new: 6 withAll: 10328) at: 2.
		^ #(1 2 3 'hello' false true nil #new)
	]
	
	testInteger [
		"Test integer types"
		| x y z |
		((2 raisedTo: 3) ~= 8) ifTrue: [self fail].
		((x := 100 / 10) ~= 10) ifTrue: [self fail].
		((y := 1 / 3) isMemberOf: Fraction) ifFalse: [self fail].
		z := SmallInteger largest.
		y := z bitShift: -30.
		x := ((16r10FF bitAnd: 16rB010) bitOr: 32) bitXor: 33.
		x := 139302 quo: -234.
		z := 1229 // 14.
		y := 1229 \\ 14.
		y := 1000 * 4 * 2.
		x := 1 + 2 - 100 + 105.
		(x < 4000 and: [x > 2]) ifFalse: [self fail].
		(x >= 0 and: [x <= 8])  ifFalse: [self fail].
		(x = 8 and: [x ~= 12359303]) ifFalse: [self fail].
		1 / 4 * 2.
		((24 gcd: 32) ~= 8) ifTrue: [self fail]
	]
	
	testObject [
		"Test advanced features of Objects"
		| x y |
		((#(3 5 2) perform: #at: withArguments: #(2)) ~= 5) ifTrue: [self fail].
		(nil perform: #isNil) ifFalse: [self fail]. 
		((Array perform: #new: with: 4) size ~= 4) ifTrue: [self fail].
		x := Array basicNew: 3.
		y := Array basicNew: 2.
		x at: 1 put: y.
		(y allOwners size ~= 2) ifTrue: [self fail]
	]
	
	testFloat [
		"Test floating point types"
		| x |
		x := 12.4.
		(x exponent ~= 4) ifTrue: [self fail].
		(x fractionPart closeTo: 0.4) ifFalse: [self fail].
		(x truncated = 12) ifFalse: [self fail].
		((x + 30 * 2) closeTo: 84.8) ifFalse: [self fail].
		((x * (1 / 3)) closeTo: 4.133333) ifFalse: [self fail].
		(x > 1) ifFalse: [self fail].
		(x < 3043.24 and: [432.423 > x]) ifFalse: [self fail].
		(x <= 12.4 and: [x >= 0.332]) ifFalse: [self fail].
		(0.0 = 0.0 and: [x ~= 0.0]) ifFalse: [self fail].
		Float e + 10.23 - 3.4e-5 * 5.74e3 / 8.43e9.
		FloatD fmax / 20.0e20 * 100000.0 * FloatD fminNormalized.
		FloatD infinity; negativeInfinity; nan; emax; emin; precision; decimalDigits
	]
	
	testIterable [
		"Test iterable types"
		| a |
		a := #(9 20 122 9 9 4 2 0 2 9 10 20 30 1).
		(a anySatisfy: [:elem | elem = 20]) ifFalse: [self fail].
		(a allSatisfy: [:elem | elem < 10]) ifTrue:  [self fail].
	   ((a count: 	   [:elem | elem = 9 ]) ~= 4) ifTrue: [self fail]
	]
		
	testByteArray [
		"Test byte array types"
		| a |
		a := ByteArray with: 0 with: 4 with: 5.
		((a indexOf: 5 startingAt: 1) ~= 3) ifTrue: [self fail].
		((a indexOf: 0 startingAt: 3) ~= 0) ifTrue: [self fail]
	]
	
	testCharArray [
		"Test character array types"
		'This is a long example string' contractTo: 12.
		'hello' asUppercase
	]		
	
	testStream [
		"Test stream types"
		| x s |
		s := 'This is a test write string'.
		x := WriteStream on: (Array new: 2).
		x nextPutAll: s.
		(x contents size ~= s size) ifTrue: [self fail].
		x := ReadStream on: 'This is a test read string'.
		21 timesRepeat: [x next].
		(x peek ~= $t) ifTrue: [self fail]
	]
	
	testException [
		"Test exception handling"
		Exception new
	]
]
