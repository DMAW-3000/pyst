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
				testStream;
				testSuper;
				testArray;
				testInteger;
				testObject;
				testFloat;
				testByteArray;
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
		a2 at: 1.
		a1 at: 1
	]
	
	testClass [
		"Test class behavior"
		Collection isReadOnly.
		(Array new: 1) isReadOnly.
		TestSuite testClassVar: #(10 20 30).
		TestSuite testClassVar at: 3.
		^true isKindOf: false class
	]
	
	testCharacter [
		"Test Character objects"
		$A isDigit: 16. $E isVowel.
		Character space isSeparator. $! isPunctuation.
		$1 isDigit. $8 isLetter. $T isAlphaNumeric.
		$A asLowercase isUppercase.
		$b asUppercase isUppercase.
		$N = $r. $X = $X
	]
		
	testBlock [
        "Test block closures"
		[:x | true and: [x]] value: false.
		[:x | true and: [x]] cull: false cull:false.
		[:x :y :z | x + y - z ] valueWithArguments: #(5 22 7).
		true ifTrue: [ | r s | r := false. s := true].
		[:a | | x | x := a] value: #nil
    ]
	
	testStream [
		"Test stream types"
		| x |
		#testSym size.
		'test string' size.
		x := WriteStream on: (Array new: 2).
		x nextPutAll: 'This is a test write string'.
		x := ReadStream on: 'This is a test read string'.
		21 timesRepeat: [x next]
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
		b at: 1; at: 2; at: 5.
		a at: 2 put: 10.
		a at: 3 put: 11.
		a at: 2; at: 3.
		y := #(1 2 3 4 10).
		x := Array new: y size.
		x replaceFrom: 1 to: x size with: y startingAt: 1.
		(a := Array new: 6 withAll: 10328) at: 2.
		^ #(1 2 3 'hello' false true nil #new)
	]
	
	testInteger [
		"Test integer types"
		| x y z |
		x := 100 / 10.
		y := 1 / 3.
		z := SmallInteger largest.
		y := z bitShift: -30.
		x := ((16r10FF bitAnd: 16rB010) bitOr: 32) bitXor: 33.
		x := 139302 quo: -234.
		z := 1229 // 14.
		y := 1229 \\ 14.
		y := 1000 * 4 * 2.
		x := 1 + 2 - 100 + 105.
		x < 4000 and: [x > 2].
		x >= 0 and: [x <= 8].
		^x = 8 and: [x ~= 12359303].
		1 / 4 * 2.
		^24 gcd: 32
	]
	
	testObject [
		"Test advanced features of Objects"
		| x y |
		#(3 5 2) perform: #at: withArguments: #(2).
		nil perform: #isNil. Array perform: #new: with: 4.
		x := Array basicNew: 3.
		y := Array basicNew: 2.
		x at: 1 put: y.
		y allOwners
	]
	
	testFloat [
		"Test floating point types"
		| x |
		x := 12.4.
		x < 3043.24 and: [432.423 > x].
		x <= 12.4 and: [x >= 0.332].
		0.0 = 0.0 and: [x ~= 0.0].
		Float e + 10.23 - 3.4e-5 * 5.74e3 / 8.43e9.
		FloatD fmax / 20.0e20 * 100000.0 * FloatD fminNormalized.
		FloatD infinity; negativeInfinity; nan; emax; emin; precision; decimalDigits
	]
	
	testByteArray [
		"Test byte array types"
		| a |
		a := ByteArray with: 0 with: 4 with: 5.
		a indexOf: 5 startingAt: 1.
		a indexOf: 0 startingAt: 3
	]
	
	testException [
		"Test exception handling"
		Exception new
	]
]
